from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=List[schemas.BusinessUnitViewBase])
def create_business_unit(
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        business_unit = models.BusinessUnit(
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
                f"Failed to initialize Business Unit model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(business_unit)
        db.commit()
        db.refresh(business_unit)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Business Unit creation")
    try:
        crud.audit_log(
            db,
            "Business Unit",
            business_unit.business_unit_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        business_unit_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.entity_status == "Active")
            .all()
        )
        return business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Business Unit view.",
        )


@router.get("/", response_model=List[schemas.BusinessUnitViewBase])
def list_business_units(db: Session = Depends(get_db)):
    try:
        business_unit_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.entity_status == "Active")
            .all()
        )
        return business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Business Unit list.",
        )


@router.get("/{id}", response_model=schemas.BusinessUnitViewBase)
def get_business_unit(id: str, db: Session = Depends(get_db)):
    try:
        business_unit_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.business_unit_id == id)
            .first()
        )
        if not business_unit_view:
            raise HTTPException(status_code=404, detail="Business Unit not found")
        return business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Business Unit details.",
        )


@router.put("/{id}", response_model=schemas.BusinessUnitViewBase)
def update_business_unit(
    id: str,
    payload: schemas.BusinessUnitUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        business_unit = (
            db.query(models.BusinessUnit)
            .filter(models.BusinessUnit.business_unit_id == id)
            .first()
        )
        if not business_unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business Unit not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Business Unit for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(business_unit, key):
                continue
            setattr(business_unit, key, value)
        business_unit.updated_at = now_utc()
        business_unit.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(business_unit)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Business Unit update")
    try:
        crud.audit_log(
            db,
            entity_type="BusinessUnit",
            entity_id=business_unit.business_unit_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        business_unit_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.business_unit_id == id)
            .first()
        )
        return business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Business Unit view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.BusinessUnitViewBase])
def archive_business_unit(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        business_unit = (
            db.query(models.BusinessUnit)
            .filter(models.BusinessUnit.business_unit_id == id)
            .first()
        )
        if not business_unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business Unit not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Business Unit for update.",
        )
    try:
        business_unit.entity_status = "Archived"
        business_unit.updated_at = now_utc()
        business_unit.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(business_unit)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Business Unit update")
    try:
        crud.audit_log(
            db,
            entity_type="BusinessUnit",
            entity_id=business_unit.business_unit_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        business_unit_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.entity_status == "Active")
            .all()
        )
        return business_unit_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Business Unit view after update.",
        )
