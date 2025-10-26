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

# Assumes the client will hit /user/token, as defined in the main app's router prefix
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

# Initialize without a prefix; the prefix /user is applied in the main application
router = APIRouter()

# In-memory OTP cache
# Stores data using the unique user_id as the key
otp_cache = {}  # {user_id: {"otp": "123456", "expires": datetime}} 

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
        # The subject ('sub') is the full_name, used for lookup
        full_name: str = payload.get("sub")
        if not full_name:
            raise ValueError("Token missing subject")
        return full_name
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def generate_next_user_id(db: Session) -> str:
    # Uses models.User.user_id
    last_user = db.query(models.User).order_by(models.User.user_id.desc()).first()
    
    if not last_user or not last_user.user_id or '-' not in last_user.user_id:
        return "USR-001"
    
    try:
        prefix, number_str = last_user.user_id.split('-')
        number = int(number_str)
    except (ValueError, IndexError):
        prefix = "USR"
        number = 0
        
    new_number = number + 1
    return f"{prefix}-{new_number:03d}"

def get_user_by_token(token: str, db: Session) -> models.User:
    full_name = decode_token(token) 
    # Uses models.User.full_name
    user = db.query(models.User).filter(models.User.full_name == full_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ------------------ ROUTES ------------------

@router.post("/register", status_code=201)
def register_user(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    # Uses models.User.full_name
    if db.query(models.User).filter(models.User.full_name == payload.full_name).first():
        raise HTTPException(status_code=400, detail="Username (full_name) already exists")

    # Uses models.User.email_address
    if db.query(models.User).filter(models.User.email_address == payload.email_address).first():
        raise HTTPException(status_code=400, detail="Email already exists for another user")

    # (Employee check commented out as per your last code block)

    new_user_id = generate_next_user_id(db)
    new_user = models.User(
        user_id=new_user_id, 
        full_name=payload.full_name, 
        password=hash_password(payload.password),
        email_address=payload.email_address, 
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user_id}

# --- Login Form ---
class SimpleLoginForm:
    def __init__(
        self,
        username: str = Form(..., description="Your username (full_name)"),
        password: str = Form(..., description="Your password"),
    ):
        self.username = username
        self.password = password

@router.post("/token")
def login_for_access_token(
    form_data: SimpleLoginForm = Depends(),
    db: Session = Depends(get_db),
):
    # Uses models.User.full_name
    user = db.query(models.User).filter(models.User.full_name == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username (full_name) or password"
        )

    access_token = create_access_token(data={"sub": user.full_name})
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------ OTP FLOW ------------------

@router.post("/request-otp")
def request_otp(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    full_name = decode_token(token) 
    # Uses models.User.full_name
    user = db.query(models.User).filter(models.User.full_name == full_name).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found or token invalid")

    otp = generate_otp()
    expiry = datetime.utcnow() + timedelta(minutes=5)
    
    # Stores OTP using the unique 'user_id'
    otp_cache[user.user_id] = {"otp": otp, "expires": expiry} 
    
    print(f"[DEBUG] OTP for User ID {user.user_id} ({user.full_name}): {otp}") 
    
    return {"message": f"OTP sent successfully (mocked) to {user.email_address}"}

    
@router.post("/verify-otp", response_model=schemas.UserLoginResponse)
def verify_otp(
    response: Response,
    username: str = Form(...), # Maps to full_name
    otp: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1. Find the user by full_name
    user = db.query(models.User).filter(models.User.full_name == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Retrieves OTP using the unique 'user_id' (FIXED)
    record = otp_cache.get(user.user_id) 
    
    if not record or record["otp"] != otp or datetime.utcnow() > record["expires"]:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # 3. Clear OTP after use, using user_id
    del otp_cache[user.user_id] 

    token = create_access_token({"sub": user.full_name}) # Use full_name as subject

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax",
        path="/",
    )

    # Return the response using the correct fields
    return schemas.UserLoginResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        email_address=user.email_address,
        authToken=token,
    )

@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}