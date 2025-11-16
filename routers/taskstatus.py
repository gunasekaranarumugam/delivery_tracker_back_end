from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
            detail=f"{operation} failed due to a data constraint violation (e.g., duplicate ID or status name).",
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
    "/",
    response_model=schemas.TaskStatusRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Task Status",
)
def create_task_status(
    payload: schemas.TaskStatusCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        print("--- Incoming Payload Data ---")
        print(payload.model_dump())
        print("-----------------------------")

        obj = models.TaskStatus(
            **payload.model_dump(),
            created_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_by=current_employee.employee_id,
            updated_at=now_utc(),
            entity_status="Active",
        )

    except Exception as e:
        print(f"Failed to initialize Task Status model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Task Status model. Check required fields or types: {e}",
        )

    print("--- ORM Object Data (Pre-Commit) ---")
    print(f"Task Status ID: {obj.task_status_id}")
    print(f"Task ID: {obj.task_id}")
    print(f"Hours Spent: {obj.hours_spent}")
    print(f"Created By: {obj.created_by}")
    print("------------------------------------")

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task Status creation")
    except Exception as e:
        handle_db_error(db, e, "Task Status creation (unexpected)")

    crud.audit_log(
        db,
        "TaskStatus",
        obj.task_status_id,
        "Create",
        changed_by=current_employee.employee_id,
    )

    obj_view = (
        db.query(models.TaskStatusView)
        .filter(models.TaskStatusView.task_status_id == obj.task_status_id)
        .first()
    )

    return obj_view


@router.get(
    "/",
    response_model=List[schemas.TaskStatusRead],
    summary="Get list of Task Statuses",
)
def list_task_statuses(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    try:
        db.query(models.TaskStatusView)

        task_statuses = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.entity_status != "ARCHIVED")
            .all()
        )

        return task_statuses

    except (DBAPIError, OperationalError) as e:
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Statuses list.",
        )
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing Task Statuses.",
        )


@router.get(
    "/{id}", response_model=schemas.TaskStatusRead, summary="Get Task Status by ID"
)
def get_task_status(id: str, db: Session = Depends(get_db)):
    try:
        obj = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == id)
            .first()
        )

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task Status not found"
            )
        return obj

    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching single Task Status.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching Task Status.",
        )


@router.put(
    "/{id}", response_model=schemas.TaskStatusRead, summary="Update Task Status"
)
def update_task_status(
    id: str,
    payload: schemas.TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        obj = (
            db.query(models.TaskStatus)
            .filter(models.TaskStatus.task_status_id == id)
            .first()
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task Status not found"
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Task Status for update.",
        )

    try:
        for k, v in payload.model_dump().items():
            setattr(obj, k, v)
        obj.updated_at = now_utc()
        obj.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )

    try:
        db.commit()
        db.refresh(obj)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task Status update")
    except Exception as e:
        handle_db_error(db, e, "Task Status update (unexpected)")

    try:
        obj_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == obj.task_status_id)
            .first()
        )
        return obj_view if obj_view else obj
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Type view after update.",
        )

    crud.audit_log(
        db,
        "TaskStatus",
        obj.task_status_id,
        "Update",
        changed_by=current_employee.employee_id,
    )


@router.patch("/{id}/archive")
def archive_task_status(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    status = (
        db.query(models.TaskStatus)
        .filter(models.TaskStatus.task_status_id == id)
        .first()
    )
    if not status:
        raise HTTPException(status_code=404, detail="TaskStatus not found")

    status.entity_status = "ARCHIVED"
    status.updated_at = now_utc()
    status.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(status)

    return {
        "message": "TaskStatus archived successfully",
        "status_id": status.task_status_id,
    }
