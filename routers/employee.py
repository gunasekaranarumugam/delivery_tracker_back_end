from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
from datetime import datetime, timezone, timedelta
import random, string
from fastapi.security import OAuth2PasswordRequestForm

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from fastapi.security import OAuth2PasswordBearer
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

# ==========================================================
# ----------------- Helpers -----------------
# ==========================================================

def generate_employee_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def now_utc():
    return datetime.now(timezone.utc)

# ==========================================================
# ----------------- JWT CONFIG -----------------
# ==========================================================

SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # 🔐 Replace with a secure value!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

TOKEN_BLACKLIST = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/Employees/login")

# ==========================================================
# ----------------- Password Hashing -----------------
# ==========================================================

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# ==========================================================
# ----------------- JWT Helper Functions -----------------
# ==========================================================

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    print("🔑 Token received:", token)  # DEBUG
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError as e:
        print("❌ JWTError:", e)
        raise HTTPException(status_code=401, detail="Invalid token")





"""def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    email = decode_access_token(token)
    employee = db.query(models.Employee).filter(models.Employee.employee_email_address == email).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee"""

def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    email = decode_access_token(token)
    employee = db.query(models.Employee).filter(
        models.Employee.employee_email_address == email
    ).first()

  

    return employee


# ==========================================================
# ----------------- Error Handling -----------------
# ==========================================================

def handle_db_error(db: Session, e: Exception, operation: str):
    db.rollback()
    if isinstance(e, IntegrityError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{operation} failed due to a data constraint violation.")
    if isinstance(e, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{operation} failed: Database operational error.")
    if isinstance(e, DBAPIError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{operation} failed: Database error.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error during {operation}.")

# ==========================================================
# ----------------- CRUD Endpoints -----------------
# ==========================================================

@router.post("/", response_model=schemas.EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: schemas.EmployeeRegister,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    try:
        employee = models.Employee(
            employee_id=payload.employee_id or generate_employee_id(),
            employee_full_name=payload.employee_full_name,
            employee_email_address=payload.employee_email_address,
            password=hash_password(payload.password),
            business_unit_id=payload.business_unit_id,
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            entity_status="Active",
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)

        crud.audit_log(db, "Employee", employee.employee_id, "Create", changed_by=current_employee.employee_id)

        employee_view = db.query(models.EmployeeView).filter(models.EmployeeView.employee_id == employee.employee_id).first()
        return employee_view
    except Exception as e:
        handle_db_error(db, e, "Employee creation")


@router.get("/", response_model=List[schemas.EmployeeRead])
def list_employees(db: Session = Depends(get_db)):
    try:
        return db.query(models.EmployeeView).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing employees: {str(e)}")


@router.get("/{id}", response_model=schemas.EmployeeRead)
def get_employee(id: str, db: Session = Depends(get_db)):
    employee_view = db.query(models.EmployeeView).filter(models.EmployeeView.employee_id == id).first()
    if not employee_view:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_view



@router.put("/{id}", response_model=schemas.EmployeeRead)
def update_employee(
    id: str, 
    payload: schemas.EmployeeUpdate, 
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    try:
        employee = db.query(models.Employee).filter(models.Employee.employee_id == id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Apply updates
        for key, value in payload.model_dump(exclude_unset=True).items():
            if key == "password":
                setattr(employee, key, hash_password(value))
            else:
                setattr(employee, key, value)

        employee.updated_at = now_utc()
        employee.updated_by = current_employee.employee_id

        db.commit()
        db.refresh(employee)

        # Audit log
        crud.audit_log(
            db,
            entity_type="Employee",
            entity_id=employee.employee_id,
            action="Update",
            changed_by=current_employee.employee_id
        )

        # Fetch full view (just like BU update/delete)
        employee_view = db.query(models.EmployeeView).filter(
            models.EmployeeView.employee_id == employee.employee_id
        ).first()

        if not employee_view:
            raise HTTPException(status_code=404, detail="Employee view not found after update")

        return employee_view

    except Exception as e:
        handle_db_error(db, e, "Employee update")




# ============================
# PATCH Employee
# ============================
@router.patch("/{id}/archive")
def archive_employee(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    # Fetch Employee
    employee = db.query(models.Employee).filter(models.Employee.employee_id == id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Soft delete / archive
    employee.entity_status = "ARCHIVED"
    employee.updated_at = now_utc()
    employee.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(employee)

    return {"message": "Employee archived successfully", "employee_id": employee.employee_id}







# ==========================================================
# ----------------- Login / Logout -----------------
# ==========================================================

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=schemas.EmployeeLoginResponse)
def login_employee(
    form_data: OAuth2PasswordRequestForm = Depends(),  # OAuth2 form
    db: Session = Depends(get_db)
):
    # Fetch employee by email
    employee = db.query(models.Employee).filter(
        models.Employee.employee_email_address == form_data.username
    ).first()

    # Employee does not exist
    if not employee:
        raise HTTPException(status_code=401, detail="Employee not found")

    # Employee exists but is archived
    if employee.entity_status != "Active":
        raise HTTPException(status_code=401, detail="Employee not found  and cannot login")

    # Verify password
    if not verify_password(form_data.password, employee.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    token = create_access_token(data={"sub": employee.employee_email_address})

    return schemas.EmployeeLoginResponse(
        employee_id=employee.employee_id,
        employee_full_name=employee.employee_full_name,
        employee_email_address=employee.employee_email_address,
        auth_token=token
    )

@router.post("/logout")
def logout_employee(token: str = Depends(oauth2_scheme)):
    TOKEN_BLACKLIST.add(token)
    return {"message": "Logout successful"}
