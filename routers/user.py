from fastapi import (
    APIRouter, Depends, HTTPException, Form, Response, status
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import random

from main import models, schemas
from main.database import get_db

# ------------------ CONFIG ------------------

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

router = APIRouter()

# In-memory OTP cache
otp_cache = {}  # {username: {"otp": "123456", "expires": datetime}}

# ------------------ UTILITIES ------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed: str) -> bool:
    return pwd_context.verify(plain_password, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise ValueError("Token missing subject")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def generate_next_user_id(db: Session) -> str:
    last_user = db.query(models.User).order_by(models.User.UserId.desc()).first()
    if not last_user or not last_user.UserId or '-' not in last_user.UserId:
        return "USR-001"
    try:
        prefix, number_str = last_user.UserId.split('-')
        number = int(number_str)
    except (ValueError, IndexError):
        prefix = "USR"
        number = 0
    new_number = number + 1
    return f"{prefix}-{new_number:03d}"

def get_user_by_token(token: str, db: Session) -> models.User:
    username = decode_token(token)
    user = db.query(models.User).filter(models.User.UserName == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ------------------ ROUTES ------------------

@router.post("/register", status_code=201)
def register_user(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if username already exists
    if db.query(models.User).filter(models.User.UserName == payload.UserName).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if db.query(models.User).filter(models.User.emailID == payload.emailID).first():
        raise HTTPException(status_code=400, detail="Email already exists for another user")

    # Check if email matches an Employee email
    if db.query(models.Employee).filter(models.Employee.Email == payload.emailID).first():
        raise HTTPException(status_code=400, detail="Email cannot match an Employee's email")

    new_user_id = generate_next_user_id(db)
    new_user = models.User(
        UserId=new_user_id,
        UserName=payload.UserName,
        password=hash_password(payload.password),
        emailID=payload.emailID,
        FirstName=payload.FirstName,
        lastName=payload.lastName,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "UserId": new_user_id}

# --- Login Form ---
class SimpleLoginForm:
    def __init__(
        self,
        username: str = Form(..., description="Your username"),
        password: str = Form(..., description="Your password"),
    ):
        self.username = username
        self.password = password

@router.post("/token")
def login_for_access_token(
    form_data: SimpleLoginForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.UserName == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": user.UserName})
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------ OTP FLOW ------------------

@router.post("/request-otp")
def request_otp(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    username = decode_token(token)
    user = db.query(models.User).filter(models.User.UserName == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)

    otp_cache[user.UserName] = {"otp": otp, "expires": expiry}
    print(f"[DEBUG] OTP for {user.UserName}: {otp}")  # Simulate email sending

    return {"message": "OTP sent successfully (mocked)"}

@router.post("/verify-otp", response_model=schemas.UserLoginResponse)
def verify_otp(
    response: Response,
    username: str = Form(...),
    otp: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.UserName == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = otp_cache.get(user.UserName)
    if not record or record["otp"] != otp or datetime.utcnow() > record["expires"]:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    del otp_cache[user.UserName]  # Clear OTP after use

    token = create_access_token({"sub": user.UserName})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax",
        path="/",
    )

    return schemas.UserLoginResponse(
        userName=user.UserName,
        emailID=user.emailID,
        FirstName=user.FirstName or "",
        lastName=user.lastName or "",
        authToken=token,
        UserId=user.UserId,
    )

@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}
