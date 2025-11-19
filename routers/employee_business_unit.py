from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=List[schemas.EmployeeBusinessUnitViewBase])
def create_employee_business_unit(
    payload: schemas.EmployeeBusinessUnitCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        employee_business_unit = models.EmployeeBusinessUnit(
            **payload.model_dump(),
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
                f"Failed to initialize Employee Business Unit model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(employee_business_unit)
        db.commit()
        db.refresh(employee_business_unit)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee Business Unit creation")
    try:
        crud.audit_log(
            db,
            "Employee Business Unit",
            employee_business_unit.business_unit_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        employee_business_unit_view = (
            db.query(models.EmployeeBusinessUnitView)
            .filter(models.EmployeeBusinessUnitView.entity_status == "Active")
            .all()
        )
        return employee_business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Employee Business Unit view.",
        )


@router.get("/", response_model=List[schemas.EmployeeBusinessUnitViewBase])
def list_employee_business_units(db: Session = Depends(get_db)):
    try:
        employee_business_unit_view = (
            db.query(models.EmployeeBusinessUnitView)
            .filter(models.EmployeeBusinessUnitView.entity_status == "Active")
            .all()
        )
        return employee_business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Employee Business Unit list.",
        )


@router.get("/{id}", response_model=schemas.EmployeeBusinessUnitViewBase)
def get_employee_business_unit(id: str, db: Session = Depends(get_db)):
    try:
        employee_business_unit_view = (
            db.query(models.EmployeeBusinessUnitView)
            .filter(models.EmployeeBusinessUnitView.business_unit_id == id)
            .first()
        )
        if not employee_business_unit_view:
            raise HTTPException(status_code=404, detail="Business Unit not found")
        return employee_business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Employee Business Unit details.",
        )


@router.put("/{id}", response_model=schemas.EmployeeBusinessUnitViewBase)
def update_employee_business_unit(
    id: str,
    payload: schemas.EmployeeBusinessUnitUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        employee_business_unit = (
            db.query(models.EmployeeBusinessUnit)
            .filter(models.EmployeeBusinessUnit.business_unit_id == id)
            .first()
        )
        if not employee_business_unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee Business Unit not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Employee Business Unit for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(employee_business_unit, key):
                continue
            setattr(employee_business_unit, key, value)
        employee_business_unit.updated_at = now_utc()
        employee_business_unit.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(employee_business_unit)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee Business Unit update")
    try:
        crud.audit_log(
            db,
            entity_type="EmployeeBusinessUnit",
            entity_id=employee_business_unit.business_unit_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        employee_business_unit_view = (
            db.query(models.EmployeeBusinessUnitView)
            .filter(models.EmployeeBusinessUnitView.business_unit_id == id)
            .first()
        )
        return employee_business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Employee Business Unit view after update.",
        )


@router.patch(
    "/{id}/archive", response_model=List[schemas.EmployeeBusinessUnitViewBase]
)
def archive_business_unit(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        employee_business_unit = (
            db.query(models.EmployeeBusinessUnit)
            .filter(models.EmployeeBusinessUnit.business_unit_id == id)
            .first()
        )
        if not employee_business_unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee Business Unit not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Business Unit for update.",
        )
    try:
        employee_business_unit.entity_status = "Archived"
        employee_business_unit.updated_at = now_utc()
        employee_business_unit.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(employee_business_unit)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Employee Business Unit update")
    try:
        crud.audit_log(
            db,
            entity_type="EmployeeBusinessUnit",
            entity_id=employee_business_unit.business_unit_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        employee_business_unit_view = (
            db.query(models.EmployeeBusinessUnitView)
            .filter(models.EmployeeBusinessUnitView.entity_status == "Active")
            .all()
        )
        return employee_business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Employee Business Unit view after update.",
        )
