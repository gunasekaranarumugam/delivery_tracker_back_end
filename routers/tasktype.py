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
            detail=f"{operation} failed due to a data constraint violation (e.g., duplicate ID or name).",
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
    response_model=schemas.TaskTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Task Type",
)
def create_task_type(
    payload: schemas.TaskTypeCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        obj = models.TaskType(
            task_type_id=payload.task_type_id,
            task_type_Name=payload.task_type_Name,
            task_type_description=payload.task_type_description,
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_at=now_utc(),
            entity_status="Active",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize Task Type model.",
        )

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task Type creation")
    except Exception as e:
        handle_db_error(db, e, "Task Type creation (unexpected)")

    obj_view = (
        db.query(models.TaskTypeView)
        .filter(models.TaskTypeView.task_type_id == obj.task_type_id)
        .first()
    )

    crud.audit_log(db, "TaskType", obj.task_type_id, "Create", changed_by="SYSTEM")
    return obj_view


@router.get(
    "/",
    response_model=List[schemas.TaskTypeRead],
    summary="Get list of Task Type records",
)
def list_task_types(
    limit: int = Query(100, ge=1), offset: int = 0, db: Session = Depends(get_db)
):
    try:
        return (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.entity_status != "ARCHIVED")
            .all()
        )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Task Types list.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing Task Types.",
        )


@router.get("/{id}", response_model=schemas.TaskTypeRead, summary="Get Task Type by ID")
def get_task_type(id: str, db: Session = Depends(get_db)):
    try:
        obj = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.task_type_id == id)
            .first()
        )

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task Type not found"
            )
        return obj

    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching single Task Type.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching Task Type.",
        )


@router.put(
    "/{id}", response_model=schemas.TaskTypeRead, summary="Update Task Type record"
)
def update_task_type(
    id: str,
    payload: schemas.TaskTypeUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        obj = (
            db.query(models.TaskType).filter(models.TaskType.task_type_id == id).first()
        )
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task Type not found"
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Task Type for update.",
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
        handle_db_error(db, e, "Task Type update")
    except Exception as e:
        handle_db_error(db, e, "Task Type update (unexpected)")

    crud.audit_log(db, "TaskType", obj.task_type_id, "Update", changed_by="SYSTEM")

    try:
        obj_view = (
            db.query(models.TaskTypeView)
            .filter(models.TaskTypeView.task_type_id == obj.task_type_id)
            .first()
        )
        return obj_view if obj_view else obj
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Task Type view after update.",
        )


@router.patch("/{id}/archive")
def archive_task_type(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    task_type = (
        db.query(models.TaskType).filter(models.TaskType.task_type_id == id).first()
    )
    if not task_type:
        raise HTTPException(status_code=404, detail="TaskType not found")

    task_type.entity_status = "ARCHIVED"
    task_type.updated_at = now_utc()
    task_type.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(task_type)

    return {
        "message": "TaskType archived successfully",
        "task_type_id": task_type.task_type_id,
    }
