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


@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task = models.Task(
            **payload.model_dump(exclude_unset=True),
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_at=now_utc(),
            entity_status="Active",
        )
        print(task)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize Task model.",
        )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task creation")
    except Exception as e:
        handle_db_error(db, e, "Task creation (unexpected)")

    try:
        task_view = (
            db.query(models.TaskView)
            .filter(models.TaskView.task_id == task.task_id)
            .first()
        )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task view after creation.",
        )

    crud.audit_log(
        db, "Task", task.task_id, "Create", changed_by=current_employee.employee_id
    )
    return task_view if task_view else task


@router.get("/", response_model=List[schemas.TaskRead])
def list_tasks(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        return (
            db.query(models.TaskView)
            .filter(models.TaskView.entity_status != "ARCHIVED")
            .all()
        )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Tasks list.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing Tasks.",
        )


@router.get("/{id}", response_model=schemas.TaskRead)
def get_task(id: str, db: Session = Depends(get_db)):
    try:
        task = db.query(models.TaskView).filter(models.TaskView.task_id == id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching single Task.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching Task.",
        )


@router.put("/{id}", response_model=schemas.TaskRead)
def update_task(
    id: str,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    action = "Update"

    try:
        task = db.query(models.Task).filter(models.Task.task_id == id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Task for update.",
        )

    if not task:
        action = "Create"
        try:
            task = models.Task(
                task_id=id,
                **payload.model_dump(exclude_unset=True),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=now_utc(),
                updated_at=now_utc(),
                entity_status="Active",
            )
            db.add(task)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize new Task model.",
            )
    else:
        try:
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(task, key, value)
            task.updated_at = now_utc()
            task.updated_by = current_employee.employee_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply update payload: {e}",
            )

    try:
        db.commit()
        db.refresh(task)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, f"Task {action.lower()}")
    except Exception as e:
        handle_db_error(db, e, f"Task {action.lower()} (unexpected)")

    crud.audit_log(
        db, "Task", task.task_id, action, changed_by=current_employee.employee_id
    )

    try:
        task_view = (
            db.query(models.TaskView)
            .filter(models.TaskView.task_id == task.task_id)
            .first()
        )
        return task_view if task_view else task
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task view after update.",
        )


@router.patch("/{id}/archive")
def archive_task(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    task = db.query(models.Task).filter(models.Task.task_id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.entity_status = "ARCHIVED"
    task.updated_at = now_utc()
    task.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(task)

    return {"message": "Task archived successfully", "task_id": task.task_id}
