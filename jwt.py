from fastapi import FastAPI, Depends, HTTPException, status, Form, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
import random

app = FastAPI()

users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpass",
        "otp": None,
        "otp_expiry": None
    }
}

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str


def create_jwt_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def generate_otp():
    return str(random.randint(100000, 999999))


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    user["otp"] = otp
    user["otp_expiry"] = expiry

    print(f"[DEBUG] OTP for {username} is: {otp}")

    return {"message": "OTP sent (check console)"}


@app.post("/verify-otp")
def verify_otp(response: Response, username: str = Form(...), otp: str = Form(...)):
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["otp"] != otp or datetime.utcnow() > user["otp_expiry"]:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user["otp"] = None
    user["otp_expiry"] = None

    token = create_jwt_token({"sub": username})

    # Set token as HttpOnly cookie, accessible on all paths
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    return {"message": "OTP verified, logged in successfully"}


@app.get("/me", response_model=User)
def get_me(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    username = verify_jwt_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"username": username}
