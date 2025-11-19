from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=List[schemas.TaskViewBase])
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task = models.Task(
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
                f"Failed to initialize Task model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task creation")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Task creation (unexpected)")
    try:
        crud.audit_log(
            db,
            "Task",
            task.task_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_view = (
            db.query(models.TaskView)
            .filter(models.TaskView.entity_status == "Active")
            .all()
        )
        return task_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Task view.",
        )


@router.get("/", response_model=List[schemas.TaskViewBase])
def list_tasks(db: Session = Depends(get_db)):
    try:
        task_view = (
            db.query(models.TaskView)
            .filter(models.TaskView.entity_status == "Active")
            .all()
        )
        return task_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task list.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing Task: {e}",
        )


@router.get("/{id}", response_model=schemas.TaskViewBase)
def get_task(id: str, db: Session = Depends(get_db)):
    try:
        task_view = (
            db.query(models.TaskView).filter(models.TaskView.task_id == id).first()
        )
        if not task_view:
            raise HTTPException(status_code=404, detail="Task not found")
        return task_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Task details.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching Task details: {e}",
        )


@router.put("/{id}", response_model=schemas.TaskViewBase)
def update_task(
    id: str,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task = db.query(models.Task).filter(models.Task.task_id == id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(task, key):
                continue
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
        db.rollback()
        handle_db_error(db, e, "Task update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Task update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Task",
            entity_id=task.task_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_view = (
            db.query(models.TaskView).filter(models.TaskView.task_id == id).first()
        )
        return task_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.TaskViewBase])
def archive_task(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task = db.query(models.Task).filter(models.Task.task_id == id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task for update.",
        )
    try:
        task.entity_status = "Archived"
        task.updated_at = now_utc()
        task.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Task update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Task",
            entity_id=task.task_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_view = (
            db.query(models.TaskView)
            .filter(models.TaskView.entity_status == "Active")
            .all()
        )
        return task_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task view after update.",
        )
