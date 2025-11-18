from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from main import models
from main.database import get_db
from main.utils import now_utc


router = APIRouter()


SECRET_KEY = "YOUR_SECRET_KEY_HERE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

TOKEN_BLACKLIST = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = now_utc() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_employee(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    email = decode_access_token(token)
    employee = (
        db.query(models.Employee)
        .filter(models.Employee.employee_email_address == email)
        .first()
    )
    return employee


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


@router.post("/")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    employee = (
        db.query(models.Employee)
        .filter(models.Employee.employee_email_address == form_data.username)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(form_data.password, employee.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if getattr(employee, "is_archived", False):
        raise HTTPException(
            status_code=403, detail="Employee is archived and cannot login"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.employee_email_address},
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "employee_id": employee.employee_id,
        "employee_full_name": employee.employee_full_name,
        "employee_email_address": employee.employee_email_address,
    }


@router.post("/logout")
def logout_employee(token: str = Depends(oauth2_scheme)):
    TOKEN_BLACKLIST.add(token)
    return {"message": "Logout successful"}
