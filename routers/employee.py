from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .login import get_current_employee, hash_password


router = APIRouter()


@router.post("/", response_model=schemas.EmployeeViewBase)
def create_employee(
    payload: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        employee = models.Employee(
            employee_id=payload.employee_id,
            employee_full_name=payload.employee_full_name,
            employee_email_address=payload.employee_email_address,
            password=hash_password(payload.password),
            created_at=now_utc(),
            created_by=current_employee.employee_id,
            updated_at=now_utc(),
            updated_by=current_employee.employee_id,
            entity_status="Active",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Failed to initialize Employee model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee creation")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Employee creation (unexpected)")
    try:
        crud.audit_log(
            db,
            "Employee",
            employee.employee_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        employee_view = (
            db.query(models.EmployeeView)
            .filter(models.EmployeeView.entity_status == "Active")
            .all()
        )
        return employee_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Employee view.",
        )


@router.get("/", response_model=List[schemas.EmployeeViewBase])
def list_employees(db: Session = Depends(get_db)):
    try:
        employee_view = (
            db.query(models.EmployeeView)
            .filter(models.EmployeeView.entity_status == "Active")
            .all()
        )
        return employee_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Employee list.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing Employee: {e}",
        )


@router.get("/{id}", response_model=schemas.EmployeeViewBase)
def get_employee(id: str, db: Session = Depends(get_db)):
    try:
        employee_view = (
            db.query(models.EmployeeView)
            .filter(models.EmployeeView.employee_id == id)
            .first()
        )
        if not employee_view:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Employee details.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching Employee details: {e}",
        )


@router.put("/{id}", response_model=schemas.EmployeeViewBase)
def update_employee(
    id: str,
    payload: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        employee = (
            db.query(models.employee).filter(models.employee.employee_id == id).first()
        )
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Employee for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(employee, key):
                continue
            if key == "password":
                setattr(employee, key, hash_password(value))
            else:
                setattr(employee, key, value)
        employee.updated_at = now_utc()
        employee.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(employee)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Employee update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Employee",
            entity_id=employee.employee_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        employee_view = (
            db.query(models.EmployeeView)
            .filter(models.EmployeeView.entity_status == "Active")
            .all()
        )
        return employee_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Employee view after update.",
        )


@router.patch("/{id}/archive", response_model=schemas.EmployeeViewBase)
def archive_employee(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        employee = (
            db.query(models.employee).filter(models.employee.employee_id == id).first()
        )
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Employee for update.",
        )
    try:
        employee.entity_status = "Archived"
        employee.updated_at = now_utc()
        employee.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Employee update (unexpected)")
    try:
        db.commit()
        db.refresh(employee)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Employee update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Employee",
            entity_id=employee.employee_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        employee_view = (
            db.query(models.EmployeeView)
            .filter(models.EmployeeView.entity_status == "Active")
            .all()
        )
        return employee_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Employee view after update.",
        )
