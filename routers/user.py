from fastapi import (
    APIRouter, Depends, HTTPException, Form, Response, Cookie, Header
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import random

from main import models, schemas
from main.database import get_db

# Constants
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# NOTE: This must match the token endpoint route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

router = APIRouter()


# --- Utility Functions ---

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
        if username is None:
            raise ValueError("Token missing subject")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def generate_next_user_id(db: Session) -> str:
    last_user = db.query(models.User).order_by(models.User.UserId.desc()).first()
    if not last_user:
        return "user-001"
    number = int(last_user.UserId.split('-')[1])
    return f"user-{number + 1:03d}"


# --- User Retrieval ---

def get_user_by_token(token: str, db: Session) -> models.User:
    username = decode_token(token)
    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.userName == username)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# --- Routes ---

@router.post("/register", status_code=201)
def register_user(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.userName == payload.userName.strip()).first():
        raise HTTPException(status_code=400, detail="User already exists")

    if not db.query(models.BusinessUnit).filter_by(BUId=payload.BUId).first():
        raise HTTPException(status_code=400, detail="Invalid BUId")

    if not db.query(models.Employee).filter_by(EmployeeId=payload.EmployeeId).first():
        raise HTTPException(status_code=400, detail="Invalid EmployeeId")

    if db.query(models.User).filter(models.User.EmployeeId == payload.EmployeeId).first():
        raise HTTPException(status_code=400, detail="Employee already linked to a user")

    new_user_id = generate_next_user_id(db)
    new_user = models.User(
        UserId=new_user_id,
        userName=payload.userName.strip(),
        password=hash_password(payload.password),
        BUId=payload.BUId,
        emailID=payload.emailID,
        FirstName=payload.FirstName,
        lastName=payload.lastName,
        fullName=f"{payload.FirstName or ''} {payload.lastName or ''}".strip(),
        EmployeeId=payload.EmployeeId,
        Role=payload.Role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "UserId": new_user_id}


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.userName == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.userName})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request-otp")
def request_otp(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    username = decode_token(token)
    user = db.query(models.User).filter(models.User.userName == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.EmployeeId:
        raise HTTPException(status_code=400, detail="User not linked to employee")

    otp = generate_otp()
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.commit()

    print(f"[DEBUG] OTP for {user.userName}: {otp}")

    return {"message": "OTP sent to your email (mocked)"}


@router.post("/verify-otp", response_model=schemas.UserLoginResponse)
def verify_otp(
    response: Response,
    username: str = Form(...),
    otp: str = Form(...),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.userName == username.strip())
        .first()
    )

    if not user or user.otp != otp or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.otp = None
    user.otp_expiry = None
    db.commit()

    token = create_access_token({"sub": user.userName})

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
        userName=user.userName,
        BUId=user.BUId,
        Role=user.role_name or "",
        emailID=user.emailID,
        FirstName=user.FirstName or "",
        lastName=user.lastName or "",
        fullName=user.fullName or "",
        authToken=token,
        UserId=user.UserId,
    )


@router.get("/me", response_model=schemas.UserLoginResponse)
def get_current_user_route(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    token = access_token or (authorization[7:] if authorization and authorization.lower().startswith("bearer ") else None)

    if not token:
        raise HTTPException(status_code=401, detail="No authentication token provided")

    user = get_user_by_token(token, db)

    return schemas.UserLoginResponse(
        userName=user.userName,
        BUId=user.BUId,
        Role=user.role_name or "",
        emailID=user.emailID,
        FirstName=user.FirstName or "",
        lastName=user.lastName or "",
        fullName=user.fullName or "",
        authToken="",
        UserId=user.UserId,
    )


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}
