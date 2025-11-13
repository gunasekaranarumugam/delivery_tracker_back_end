from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
from datetime import datetime, timezone
from .employee import get_current_employee
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

# Helper function for consistent timestamp handling (using UTC-aware datetime)
def now_utc():
    # Use timezone.utc for consistency
    return datetime.now(timezone.utc)

# Helper function to handle common DB exceptions (reused logic)
def handle_db_error(db: Session, e: Exception, operation: str):
    try:
        db.rollback()
    except Exception:
        pass # Ignore errors on rollback itself
        
    if isinstance(e, IntegrityError):
        # Handle cases like duplicate primary key or foreign key violation
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{operation} failed due to a data constraint violation (e.g., duplicate ID or foreign key error)."
        )
    elif isinstance(e, OperationalError):
        # Handle cases like table non-existence or bad SQL syntax
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: Database operational error. Check the SQL syntax or connection."
        )
    elif isinstance(e, DBAPIError):
        # Handle general database connection or execution errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: A database connection or query execution error occurred."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during the {operation} operation."
        )

# ----------------------------------------------------------------------
# --- POST / (Create Task) ---
# ----------------------------------------------------------------------
@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: schemas.TaskCreate, db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)):
    try:
        task = models.Task(
            **payload.model_dump(exclude_unset=True),
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_at=now_utc(),
            entity_status="Active"
        )
        print(task) # Keep for debugging if needed, but usually removed in production code
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize Task model.")

    # Commit and refresh
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task creation")
    except Exception as e:
        handle_db_error(db, e, "Task creation (unexpected)")

    # Retrieve view for full response data
    try:
        task_view = db.query(models.TaskView).filter(models.TaskView.task_id == task.task_id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while querying Task view after creation.")


    crud.audit_log(db, "Task", task.task_id, "Create", changed_by=current_employee.employee_id)
    return task_view if task_view else task


# ----------------------------------------------------------------------
# --- GET / (List Tasks) ---
# ----------------------------------------------------------------------
@router.get("/", response_model=List[schemas.TaskRead])
def list_tasks(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        # Filter to exclude 'ARCHIVED' records and apply limit/offset
        return db.query(models.TaskView).filter(
            models.TaskView.entity_status != "ARCHIVED"
        ).all()
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching Tasks list.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while listing Tasks.")


# ----------------------------------------------------------------------
# --- GET /{id} (Get Single Task) ---
# ----------------------------------------------------------------------
@router.get("/{id}", response_model=schemas.TaskRead)
def get_task(id: str, db: Session = Depends(get_db)):
    try:
        # Query the View model for full joined data
        task = db.query(models.TaskView).filter(models.TaskView.task_id == id).first()
        
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
        
    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching single Task.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while fetching Task.")


# ----------------------------------------------------------------------
# --- PUT /{id} (Update or Create Task) ---
# ----------------------------------------------------------------------
@router.put("/{id}", response_model=schemas.TaskRead)
def update_task(id: str, payload: schemas.TaskUpdate, db: Session = Depends(get_db),current_employee: models.Employee = Depends(get_current_employee)):
    action = "Update"
    
    # 1. Retrieve the existing object
    try:
        task = db.query(models.Task).filter(models.Task.task_id == id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while retrieving Task for update.")

    # 2. Conditional Create or Update
    if not task:
        action = "Create"
        # Create if not exists (PUT-semantics)
        try:
            task = models.Task(
                task_id=id,
                **payload.model_dump(exclude_unset=True),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=now_utc(),
                updated_at=now_utc(),
                entity_status="Active"
            )
            db.add(task)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize new Task model.")
    else:
        # Update existing
        try:
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(task, key, value)
            task.updated_at = now_utc()
            task.updated_by = current_employee.employee_id
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to apply update payload: {e}")

    # 3. Commit and refresh
    try:
        db.commit()
        db.refresh(task)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, f"Task {action.lower()}")
    except Exception as e:
        handle_db_error(db, e, f"Task {action.lower()} (unexpected)")

    # 4. Audit log and response
    crud.audit_log(db, "Task", task.task_id, action, changed_by=current_employee.employee_id)
    
    # Return the full view data
    try:
        task_view = db.query(models.TaskView).filter(models.TaskView.task_id == task.task_id).first()
        return task_view if task_view else task
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while querying Task view after update.")



@router.patch("/{id}/archive")
def archive_task(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    # Fetch Task
    task = db.query(models.Task).filter(models.Task.task_id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Soft delete / archive
    task.entity_status = "ARCHIVED"
    task.updated_at = now_utc()
    task.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(task)

    return {"message": "Task archived successfully", "task_id": task.task_id}
