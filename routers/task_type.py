from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=schemas.TaskTypeViewBase)
def create_task_type(
    payload: schemas.TaskTypeCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task_type = models.TaskType(
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
                f"Failed to initialize Task Type model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(task_type)
        db.commit()
        db.refresh(task_type)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task Type creation")
    try:
        crud.audit_log(
            db,
            "TaskType",
            task_type.task_type_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_type_view = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.task_type_id == task_type.task_type_id)
            .first()
        )
        return task_type_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Task Type view.",
        )


@router.get("/", response_model=List[schemas.TaskTypeViewBase])
def list_task_type(db: Session = Depends(get_db)):
    try:
        task_type_view = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.entity_status == "Active")
            .all()
        )
        return task_type_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Type list.",
        )


@router.get("/{id}", response_model=schemas.TaskTypeViewBase)
def get_task_type(id: str, db: Session = Depends(get_db)):
    try:
        task_type_view = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.task_type_id == id)
            .first()
        )
        if not task_type_view:
            raise HTTPException(status_code=404, detail="Task Type not found")
        return task_type_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Task Type details.",
        )


@router.put("/{id}", response_model=schemas.TaskTypeViewBase)
def update_task_type(
    id: str,
    payload: schemas.TaskTypeUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task_type = (
            db.query(models.TaskType).filter(models.TaskType.task_type_id == id).first()
        )
        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task Type not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Type for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(task_type, key):
                continue
            setattr(task_type, key, value)
        task_type.updated_at = now_utc()
        task_type.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(task_type)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task Type update")
    try:
        crud.audit_log(
            db,
            entity_type="TaskType",
            entity_id=task_type.task_type_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_type_view = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.task_type_id == id)
            .first()
        )
        return task_type_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Type view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.TaskTypeViewBase])
def archive_task_type(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        task_type = (
            db.query(models.TaskType).filter(models.TaskType.task_type_id == id).first()
        )
        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task Type not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Type for update.",
        )
    try:
        task_type.entity_status = "Archived"
        task_type.updated_at = now_utc()
        task_type.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(task_type)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Task Type update")
    try:
        crud.audit_log(
            db,
            entity_type="TaskType",
            entity_id=task_type.task_type_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        task_type_view = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.entity_status == "Active")
            .all()
        )
        return task_type_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Type view after update.",
        )
