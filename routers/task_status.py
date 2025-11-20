from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=schemas.TaskStatusViewBase)
def create_task_status(
    payload: schemas.TaskStatusCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task_status = models.TaskStatus(
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
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Task Status view.",
        )


@router.get("/", response_model=List[schemas.TaskStatusViewBase])
def list_task_status(db: Session = Depends(get_db)):
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.entity_status == "Active")
            .all()
        )
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Status list.",
        )


@router.get("/{id}", response_model=schemas.TaskStatusViewBase)
def get_task_status(id: str, db: Session = Depends(get_db)):
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == id)
            .first()
        )
        if not task_status_view:
            raise HTTPException(status_code=404, detail="Task Status not found")
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Task Status details.",
        )


@router.put("/{id}", response_model=schemas.TaskStatusViewBase)
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
            detail="Database error while fetching Task Status for update.",
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
    try:
        crud.audit_log(
            db,
            entity_type="TaskStatus",
            entity_id=task_status.task_status_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.task_status_id == id)
            .first()
        )
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Status view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.TaskStatusViewBase])
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
            detail="Database error while fetching Task Status for update.",
        )
    try:
        task_status.entity_status = "Archived"
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
    try:
        crud.audit_log(
            db,
            entity_type="TaskStatus",
            entity_id=task_status.task_status_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_status_view = (
            db.query(models.TaskStatusView)
            .filter(models.TaskStatusView.entity_status == "Active")
            .all()
        )
        return task_status_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Status view after update.",
        )
