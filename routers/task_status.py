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
        task_status = models.TaskStatus(
            **payload.model_dump(),
            created_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_by=current_employee.employee_id,
            updated_at=now_utc(),
            entity_status="Active",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Failed to initialize Task Status model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(task_status)
        db.commit()
        db.refresh(task_status)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task Status creation")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Task Status creation (unexpected)")
    try:
        crud.audit_log(
            db,
            "TaskStatus",
            task_status.task_status_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == task_status.task_status_id)
            .first()
        )
        return task_status_view if task_status_view else task_status
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving created Task Status view.",
        )


@router.get(
    "/",
    response_model=List[schemas.TaskStatusRead],
    summary="Get list of Task Status",
)
def list_task_status(
    db: Session = Depends(get_db),
):
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.entity_status != "ARCHIVED")
            .all()
        )
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Status list.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing Task Statuses: {e}",
        )


@router.get(
    "/{id}",
    response_model=schemas.TaskStatusRead,
    summary="Get Task Status by ID",
)
def get_task_status(
    id: str,
    db: Session = Depends(get_db),
):
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == id)
            .first()
        )
        if not task_status_view:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task Status not found",
            )
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Status.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching Task Status: {e}",
        )


@router.put(
    "/{id}",
    response_model=schemas.TaskStatusRead,
    summary="Update Task Status",
)
def update_task_status(
    id: str,
    payload: schemas.TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task_status = (
            db.query(models.TaskStatus)
            .filter(models.TaskStatus.task_status_id == id)
            .first()
        )
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task Status not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Task Status for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(task_status, key):
                continue
            setattr(task_status, key, value)
        task_status.updated_at = now_utc()
        task_status.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(task_status)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task Status update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Task Status update (unexpected)")
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == task_status.task_status_id)
            .first()
        )
        try:
            crud.audit_log(
                db,
                "TaskStatus",
                task_status.task_status_id,
                "Update",
                changed_by=current_employee.employee_id,
            )
        except Exception:
            pass
        return task_status_view if task_status_view else task_status
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Status view after update.",
        )


@router.patch(
    "/{id}/archive",
    summary="Archive Task Status",
)
def archive_task_status(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task_status = (
            db.query(models.TaskStatus)
            .filter(models.TaskStatus.task_status_id == id)
            .first()
        )
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task Status not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Task Status for archive.",
        )
    try:
        task_status.entity_status = "ARCHIVED"
        task_status.updated_at = now_utc()
        task_status.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply archive changes: {e}",
        )
    try:
        db.commit()
        db.refresh(task_status)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task Status archive")
    except Exception as e:
        handle_db_error(db, e, "Task Status archive (unexpected)")
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == task_status.task_status_id)
            .first()
        )
        try:
            crud.audit_log(
                db,
                "TaskStatus",
                task_status.task_status_id,
                "Archive",
                changed_by=current_employee.employee_id,
            )
        except Exception:
            pass
        return task_status_view if task_status_view else task_status
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Status view after archive.",
        )
