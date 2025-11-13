from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    return datetime.now(timezone.utc)

# Helper function to handle common DB exceptions (reused logic)
def handle_db_error(db: Session, e: Exception, operation: str):
    try:
        db.rollback()
    except Exception:
        pass # Ignore errors on rollback itself
        
    if isinstance(e, IntegrityError):
        # Handle cases like duplicate primary key or unique constraint violation
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{operation} failed due to a data constraint violation (e.g., duplicate ID or status name)."
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
# --- POST / (Create Task Status) ---
# ----------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
from datetime import datetime, timezone
# Assuming now_utc() and handle_db_error are defined elsewhere in the file

# Helper function for consistent timestamp handling (ensure this is defined)
def now_utc():
    return datetime.now(timezone.utc)

# ... (router = APIRouter(), handle_db_error definition) ...

@router.post(
    "/", 
    response_model=schemas.TaskStatusRead, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a new Task Status"
)
def create_task_status(
    payload: schemas.TaskStatusCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    # 1. Instantiate the model with payload data AND audit/system data
    try:
        # Print the incoming Pydantic payload data for debugging
        print("--- Incoming Payload Data ---")
        print(payload.model_dump()) 
        print("-----------------------------")
        
        obj = models.TaskStatus(
            **payload.model_dump(),
            created_by=current_employee.employee_id, # NOTE: Change this "0" to the authenticated user's ID
            created_at=now_utc(),
            updated_by=current_employee.employee_id,
            updated_at=now_utc(),
            entity_status="Active"
        )

    except Exception as e:
        print(f"Failed to initialize Task Status model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Task Status model. Check required fields or types: {e}"
        )
    
    # Print the instantiated ORM object's key data before commit
    print("--- ORM Object Data (Pre-Commit) ---")
    print(f"Task Status ID: {obj.task_status_id}")
    print(f"Task ID: {obj.task_id}")
    print(f"Hours Spent: {obj.hours_spent}")
    print(f"Created By: {obj.created_by}")
    print("------------------------------------")

    # 2. Commit and refresh
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        # Handles errors like unique constraint violations, foreign key issues, etc.
        handle_db_error(db, e, "Task Status creation")
    except Exception as e:
        # Catches other unexpected database errors
        handle_db_error(db, e, "Task Status creation (unexpected)")

    # 3. Audit log and return
    # Record the creation action
    crud.audit_log(db, "TaskStatus", obj.task_status_id, "Create", changed_by=current_employee.employee_id)
    
    # Fetch the detailed view object to include related names (for TaskStatusRead response)
    obj_view = db.query(models.TaskStatusView).filter(
        models.TaskStatusView.task_status_id == obj.task_status_id
    ).first()

    # The view object (obj_view) has all the names (created_by_name, project_name, etc.)
    return obj_view


# ----------------------------------------------------------------------
# --- GET / (List Task Statuses) ---
# ----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[schemas.TaskStatusRead], 
    summary="Get list of Task Statuses"
)
def list_task_statuses(
    # Default limit of 100, must be greater than or equal to 1
    limit: int = Query(100, ge=1), 
    offset: int = 0,
    db: Session = Depends(get_db),
):
    try:
        # 1. Start the query on the detailed view model
        query = db.query(models.TaskStatusView)
        
        # 2. Apply the 'ARCHIVED' filter
        #query = query.filter(
        #    models.TaskStatusView.entity_status != "ARCHIVED"
        #)
        
        # 3. Apply the pagination parameters (limit and offset)
        #    Use .offset() and .limit() on the query object
        task_statuses =  db.query(models.TaskStatusView).filter(
            models.TaskStatusView.entity_status != "ARCHIVED"
        ).all()

        # 4. Return the results
        return task_statuses
        
    except (DBAPIError, OperationalError) as e:
        # Log the error for internal use, then raise a generic 500
        print(f"Database Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error while fetching Task Statuses list."
        )
    except Exception as e:
        # Log the error for internal use
        print(f"Unexpected Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while listing Task Statuses."
        )

# ----------------------------------------------------------------------
# --- GET /{id} (Get Task Status by ID) ---
# ----------------------------------------------------------------------
@router.get("/{id}", response_model=schemas.TaskStatusRead, summary="Get Task Status by ID")
def get_task_status(id: str, db: Session = Depends(get_db)):
    try:
        # Query the View model for full joined data
        obj = db.query(models.TaskStatusView).filter(models.TaskStatusView.task_status_id == id).first()
        
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Status not found")
        return obj
        
    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching single Task Status.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while fetching Task Status.")


# ----------------------------------------------------------------------
# --- PUT /{id} (Update Task Status) ---
# ----------------------------------------------------------------------
@router.put("/{id}", response_model=schemas.TaskStatusRead, summary="Update Task Status")
def update_task_status(id: str, payload: schemas.TaskStatusUpdate, db: Session = Depends(get_db),current_employee: models.Employee = Depends(get_current_employee)):
    # 1. Retrieve the existing object
    try:
        obj = db.query(models.TaskStatus).filter(models.TaskStatus.task_status_id == id).first()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Status not found")
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while retrieving Task Status for update.")

    # 2. Apply updates
    try:
        for k, v in payload.model_dump().items():
            setattr(obj, k, v)
        obj.updated_at = now_utc()
        obj.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to apply update payload: {e}")
        
    # 3. Commit and refresh
    try:
        db.commit()
        db.refresh(obj)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Task Status update")
    except Exception as e:
        handle_db_error(db, e, "Task Status update (unexpected)")

    
    try:
        obj_view = db.query(models.TaskStatusView).filter(models.TaskStatusView.task_status_id == obj.task_status_id).first()
        return obj_view if obj_view else obj
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while querying Task Type view after update.")   

    # 4. Audit log and response
    crud.audit_log(db, "TaskStatus", obj.task_status_id, "Update", changed_by=current_employee.employee_id)


@router.patch("/{id}/archive")
def archive_task_status(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    # Fetch TaskStatus
    status = db.query(models.TaskStatus).filter(models.TaskStatus.task_status_id == id).first()
    if not status:
        raise HTTPException(status_code=404, detail="TaskStatus not found")

    # Soft delete / archive
    status.entity_status = "ARCHIVED"
    status.updated_at = now_utc()
    status.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(status)

    return {"message": "TaskStatus archived successfully", "status_id": status.task_status_id}

