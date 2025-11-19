from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=List[schemas.DeliverableViewBase])
def create_deliverable(
    payload: schemas.DeliverableCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        deliverable = models.Deliverable(
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
                f"Failed to initialize Deliverable model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(deliverable)
        db.commit()
        db.refresh(deliverable)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Deliverable creation")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Deliverable Creation (unexpected)")
    try:
        crud.audit_log(
            db,
            "Deliverable",
            deliverable.deliverable_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.entity_status == "Active")
            .all()
        )
        return deliverable_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Deliverable view.",
        )


@router.get("/", response_model=List[schemas.DeliverableViewBase])
def list_deliverables(db: Session = Depends(get_db)):
    try:
        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.entity_status == "Active")
            .all()
        )
        return deliverable_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Deliverable list.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing Deliverable: {e}",
        )


@router.get("/{id}", response_model=schemas.DeliverableViewBase)
def get_deliverable(id: str, db: Session = Depends(get_db)):
    try:
        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.deliverable_id == id)
            .first()
        )
        if not deliverable_view:
            raise HTTPException(status_code=404, detail="Deliverable not found")
        return deliverable_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Deliverable details.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching Deliverable details: {e}",
        )


@router.put("/{id}", response_model=schemas.DeliverableViewBase)
def update_deliverable(
    id: str,
    payload: schemas.DeliverableUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        deliverable = (
            db.query(models.Deliverable)
            .filter(models.Deliverable.deliverable_id == id)
            .first()
        )
        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Deliverable for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(deliverable, key):
                continue
            setattr(deliverable, key, value)
        deliverable.updated_at = now_utc()
        deliverable.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(deliverable)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Deliverable update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Deliverable update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Deliverable",
            entity_id=deliverable.deliverable_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.deliverable_id == id)
            .first()
        )
        return deliverable_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Deliverable view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.DeliverableViewBase])
def archive_deliverable(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        deliverable = (
            db.query(models.Deliverable)
            .filter(models.Deliverable.deliverable == id)
            .first()
        )
        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Deliverable for update.",
        )
    try:
        deliverable.entity_status = "Archived"
        deliverable.updated_at = now_utc()
        deliverable.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Deliverable update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Deliverable update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Deliverable",
            entity_id=deliverable.deliverable_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.entity_status == "Active")
            .all()
        )
        return deliverable_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Deliverable view after update.",
        )
