from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db, handle_db_error

from .employee import get_current_employee


router = APIRouter()


def now():
    return datetime.utcnow()


@router.post("/", response_model=schemas.BusinessUnitViewBase)
def create_business_unit(
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        bu = models.BusinessUnit(
            **payload.model_dump(),
            created_at=now(),
            updated_at=now(),
            created_by=current_employee.employee_id,
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
        db.add(bu)
        db.commit()
        db.refresh(bu)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Business Unit creation")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Business Unit creation (unexpected)")
    try:
        crud.audit_log(
            db,
            "Business Unit",
            bu.business_unit_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        bu_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.business_unit_id == bu.business_unit_id)
            .first()
        )
        return bu_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving created Business Unit view.",
        )


@router.get("/", response_model=List[schemas.BusinessUnitRead])
def list_business_units(db: Session = Depends(get_db)):
    try:
        return (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.entity_status == "Active")
            .all()
        )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500, detail="Database error while fetching Business Units list."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{id}", response_model=schemas.BusinessUnitRead)
def get_business_unit(id: str, db: Session = Depends(get_db)):
    try:
        bu = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.business_unit_id == id)
            .first()
        )
        if not bu:
            raise HTTPException(status_code=404, detail="Business Unit not found")
        return bu
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500, detail="Database error while fetching Business Unit."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.put("/{id}", response_model=schemas.BusinessUnitUpdate, status_code=200)
def update_business_unit(
    id: str,
    payload: schemas.BusinessUnitUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        bu = (
            db.query(models.BusinessUnit)
            .filter(models.BusinessUnit.business_unit_id == id)
            .first()
        )

        if not bu:
            bu = models.BusinessUnit(
                business_unit_id=id,
                business_unit_name=payload.business_unit_name or "Unnamed BU",
                business_unit_head_id=payload.business_unit_head_id
                or current_employee.employee_id,
                business_unit_description=payload.business_unit_description
                or "No description",
                created_at=now(),
                updated_at=now(),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                entity_status=payload.entity_status or "Active",
            )
            db.add(bu)
            action = "Create"
        else:
            update_data = payload.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(bu, key, value)

            bu.updated_at = now()
            bu.updated_by = current_employee.employee_id
            action = "Update"

        db.commit()
        db.refresh(bu)

        bu_view = (
            db.query(models.BusinessUnitView)
            .filter(models.BusinessUnitView.business_unit_id == bu.business_unit_id)
            .first()
        )

        if not bu_view:
            raise HTTPException(
                status_code=404, detail="Business Unit view not found after update"
            )

        crud.audit_log(
            db,
            entity_type="BusinessUnit",
            entity_id=bu.business_unit_id,
            action=action,
            changed_by=current_employee.employee_id,
        )

        return bu_view

    except (DBAPIError, OperationalError):
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Database error while updating Business Unit."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.patch("/{id}/archive")
def archive_business_unit(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_employee),
):
    bu = (
        db.query(models.BusinessUnit)
        .filter(models.BusinessUnit.business_unit_id == id)
        .first()
    )
    if not bu:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    bu.entity_status = "ARCHIVED"
    bu.updated_at = now()
    bu.updated_by = current_user.employee_id

    db.commit()
    db.refresh(bu)

    return {
        "message": "Business Unit archived successfully",
        "business_unit_id": bu.business_unit_id,
    }
