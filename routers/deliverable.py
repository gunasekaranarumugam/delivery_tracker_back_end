from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db

from .employee import get_current_employee


router = APIRouter()


def now_utc():
    return datetime.now(timezone.utc)


def handle_db_error(db: Session, e: Exception, operation: str):
    try:
        db.rollback()
    except Exception:
        pass

    if isinstance(e, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{operation} failed due to a data constraint violation (e.g., duplicate ID or foreign key error).",
        )
    elif isinstance(e, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: Database operational error. Check the SQL syntax or connection.",
        )
    elif isinstance(e, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: A database connection or query execution error occurred.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during the {operation} operation.",
        )


@router.post(
    "/", response_model=schemas.DeliverableRead, status_code=status.HTTP_201_CREATED
)
def create_deliverable(
    payload: schemas.DeliverableCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        deliverable = models.Deliverable(
            **payload.model_dump(exclude_unset=True),
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_at=now_utc(),
            entity_status="Active",
        )
        db.add(deliverable)
        db.commit()
        db.refresh(deliverable)

        crud.audit_log(
            db,
            "Deliverable",
            deliverable.deliverable_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.deliverable_id == deliverable.deliverable_id)
            .first()
        )
        return deliverable_view or deliverable

    except Exception as e:
        handle_db_error(db, e, "Deliverable creation")


@router.get(
    "/",
    response_model=List[schemas.DeliverableRead],
    summary="List active Deliverables",
)
def list_deliverables(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        return (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.entity_status != "ARCHIVED")
            .all()
        )

    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Deliverables list.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing Deliverables.",
        )


@router.get("/{id}", response_model=schemas.DeliverableRead)
def get_deliverable(id: str, db: Session = Depends(get_db)):
    try:
        deliverable = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.deliverable_id == id)
            .first()
        )

        if not deliverable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found"
            )
        return deliverable

    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching single Deliverable.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching Deliverable.",
        )


"""
@router.put("/{id}", response_model=schemas.DeliverableRead)
def update_deliverable(
    id: str, 
    payload: schemas.DeliverableUpdate, 
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    try:
        deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
        print(deliverable.priority)
        action = "Update"

        if not deliverable:
            action = "Create"
            deliverable = models.Deliverable(
                deliverable_id=id,
                **{k: v for k, v in payload.model_dump(exclude_unset=True).items() if not k.endswith("_name")},
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=now_utc(),
                updated_at=now_utc(),
                entity_status="Active"
            )
            db.add(deliverable)
        else:
            
            update_data = payload.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key.endswith("_name"):
                    continue
                setattr(deliverable, key, value)

            deliverable.updated_at = now_utc()
            deliverable.updated_by = current_employee.employee_id
        
        print("Payload being updated:", payload.model_dump(exclude_unset=True))

        db.commit()
        db.refresh(deliverable)

        crud.audit_log(db, "Deliverable", deliverable.deliverable_id, action, changed_by=current_employee.employee_id)

        deliverable_view = db.query(models.DeliverableView)\
            .filter(models.DeliverableView.deliverable_id == deliverable.deliverable_id)\
            .first()
        
        print(deliverable_view.priority)

        if not deliverable_view:
            return deliverable

        return deliverable_view

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating Deliverable: {str(e)}")
     
"""


@router.put("/{id}", response_model=schemas.DeliverableRead)
def update_deliverable(
    id: str,
    payload: schemas.DeliverableUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        print("\n=== Update Deliverable Called ===")
        print(f"Deliverable ID: {id}")
        print(f"Payload received: {payload.model_dump(exclude_unset=True)}")
        print(f"Current employee: {current_employee.employee_id}")

        deliverable = (
            db.query(models.Deliverable)
            .filter(models.Deliverable.deliverable_id == id)
            .first()
        )

        if not deliverable:
            print("Deliverable not found. Creating a new one.")
            deliverable = models.Deliverable(
                deliverable_id=id,
                **payload.model_dump(exclude_unset=True),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                entity_status="Active",
            )
            db.add(deliverable)
        else:
            print("Deliverable found. Updating existing deliverable.")
            for key, value in payload.model_dump(exclude_unset=True).items():
                print(f"Updating {key} = {value}")
                setattr(deliverable, key, value)

            deliverable.updated_at = datetime.utcnow()
            deliverable.updated_by = current_employee.employee_id

        db.commit()
        db.refresh(deliverable)
        print("Database commit successful.")

        deliverable_view = (
            db.query(models.DeliverableView)
            .filter(models.DeliverableView.deliverable_id == deliverable.deliverable_id)
            .first()
        )

        print(f"Returning deliverable view: {deliverable_view.priority}")
        print("=== Update Deliverable Finished ===\n")
        return deliverable_view

    except Exception as e:
        db.rollback()
        print(f"Error updating deliverable: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update deliverable: {str(e)}"
        )


@router.patch("/{id}/archive")
def archive_deliverable(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    deliverable = (
        db.query(models.Deliverable)
        .filter(models.Deliverable.deliverable_id == id)
        .first()
    )
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    deliverable.entity_status = "ARCHIVED"
    deliverable.updated_at = now_utc()
    deliverable.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(deliverable)

    return {
        "message": "Deliverable archived successfully",
        "deliverable_id": deliverable.deliverable_id,
    }
