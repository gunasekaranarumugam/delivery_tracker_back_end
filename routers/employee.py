from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from main import models, schemas, crud
from main.database import get_db

import random
import string

def generate_employee_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


router = APIRouter()


@router.post("/", response_model=schemas.EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(payload: schemas.EmployeeRegister, db: Session = Depends(get_db)):
    employee = models.Employee(
        employee_id = payload.employee_id,
        employee_full_name=payload.employee_full_name,
        employee_email_address=payload.employee_email_address,
        password=payload.password,
        business_unit_id=payload.business_unit_id,
        
        created_by="SYSTEM",
        updated_by="SYSTEM",
        entity_status="Active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    crud.audit_log(db, "Employee", employee.employee_id, "Create", changed_by="SYSTEM")
    return employee

@router.get("/", response_model=List[schemas.EmployeeRead])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.EmployeeView).all()


@router.get("/{id}", response_model=schemas.EmployeeRead)
def get_employee(id: str, db: Session = Depends(get_db)):
    return db.query(models.Employee).filter(models.Employee.employee_id == id).first()


@router.put("/{id}", response_model=schemas.EmployeeRead)
def update_employee(id: str, payload: schemas.EmployeeRegister, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.employee_id == id).first()
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)
    employee.updated_at = datetime.utcnow()
    employee.updated_by = "SYSTEM"
    db.commit()
    db.refresh(employee)

    crud.audit_log(db, "Employee", employee.employee_id, "Update", changed_by="SYSTEM")
    return employee


@router.patch("/{id}/archive", response_model=schemas.EmployeeRead, status_code=status.HTTP_200_OK)
def patch_employee(
    id: str,
    payload: schemas.EmployeePatch,  # Schema with all optional fields
    db: Session = Depends(get_db)
):
    # Fetch employee
    employee = db.query(models.Employee).filter(models.Employee.employee_id == id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)

    # Automatically handle archiving if requested
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        employee.entity_status = "ARCHIVED"

    # Update timestamps and system info
    employee.updated_at = datetime.now()
    employee.updated_by = "SYSTEM"

    db.commit()
    db.refresh(employee)

    # Create audit log
    crud.audit_log(
        db,
        entity_type="Employee",
        entity_id=employee.employee_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return employee


