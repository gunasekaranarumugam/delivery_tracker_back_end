from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
from datetime import datetime, timezone
from .employee import get_current_employee
from main import models, schemas, crud
from main.database import get_db
from .employee import get_current_employee
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{operation} failed due to a data constraint violation (e.g., duplicate ID or foreign key error)."
        )
    elif isinstance(e, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: Database operational error. Check the SQL syntax or connection."
        )
    elif isinstance(e, DBAPIError):
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
# --- POST / (Create Issue Activity) ---
# ----------------------------------------------------------------------
@router.post("/", response_model=schemas.IssueActivityRead, status_code=status.HTTP_201_CREATED)
def create_issue_activity(payload: schemas.IssueActivityCreate, db: Session = Depends(get_db),current_employee: models.Employee = Depends(get_current_employee)):
    try:
        activity = models.IssueActivity(
            **payload.model_dump(exclude_unset=True),
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(), # Use UTC-aware timestamp
            updated_at=now_utc(),
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize Issue Activity model.")

    try:
        db.add(activity)
        db.commit()
        db.refresh(activity)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Issue Activity creation")
    except Exception as e:
        handle_db_error(db, e, "Issue Activity creation (unexpected)")

    activity_view = db.query(models.IssueActivityView).filter(
        models.IssueActivityView.issue_activity_id == activity.issue_activity_id
    ).first()

    crud.audit_log(db, "IssueActivity", activity.issue_activity_id, "Create", changed_by=current_employee.employee_id)
    return activity_view

# ----------------------------------------------------------------------
# --- GET / (List Issue Activities) ---
# ----------------------------------------------------------------------
@router.get("/", response_model=List[schemas.IssueActivityRead])
def list_issue_activities(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        # Note: Issue activities are typically listed by issue_id, but using .all() for now
        return db.query(models.IssueActivityView).all()
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching Issue Activities list.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while listing Issue Activities.")

# ----------------------------------------------------------------------
# --- GET /{id} (Get Single Issue Activity) ---
# ----------------------------------------------------------------------
@router.get("/{id}", response_model=schemas.IssueActivityRead)
def get_issue_activity(id: str, db: Session = Depends(get_db)):
    try:
        # Query the View model for joined data if available, otherwise the base model
        activity = db.query(models.IssueActivityView).filter(models.IssueActivityView.issue_activity_id == id).first()
        
        if not activity:
            # Fallback to base model query if the view is problematic or doesn't exist
            activity = db.query(models.IssueActivity).filter(models.IssueActivity.issue_activity_id == id).first()
            if not activity:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue Activity not found")
                 
        return activity
        
    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching single Issue Activity.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while fetching Issue Activity.")

# ----------------------------------------------------------------------
# --- PUT /{id} (Update or Create Issue Activity) ---
# ----------------------------------------------------------------------
@router.put("/{id}", response_model=schemas.IssueActivityRead)
def update_issue_activity(id: str, payload: schemas.IssueActivityUpdate, db: Session = Depends(get_db),current_employee: models.Employee = Depends(get_current_employee)):
    # WARNING: Typically Issue Activities should NOT be updatable as they represent chronological events.
    # We proceed with the update logic but recommend reviewing this business requirement.
    action = "Update"
    
    try:
        activity = db.query(models.IssueActivity).filter(models.IssueActivity.issue_activity_id == id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while retrieving Issue Activity for update.")

    if not activity:
        action = "Create"
        # Create if not exists (PUT-semantics)
        try:
            activity = models.IssueActivity(
                issue_activity_id=id,
                **payload.model_dump(exclude_unset=True),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=now_utc(),
                updated_at=now_utc()
            )
            db.add(activity)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize new Issue Activity model.")
    else:
        # Update existing
        try:
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(activity, key, value)
            activity.updated_at = now_utc()
            activity.updated_by = current_employee.employee_id
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to apply update payload: {e}")

    # Commit and refresh
    try:
        db.commit()
        db.refresh(activity)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, f"Issue Activity {action.lower()}")
    except Exception as e:
        handle_db_error(db, e, f"Issue Activity {action.lower()} (unexpected)")

    
    try:
        obj_view = db.query(models.IssueActivityView).filter(models.IssueActivityView.issue_activity_id == activity.issue_activity_id).first()
        return obj_view if obj_view else obj
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while querying Task Type view after update.")
    # Audit log
    crud.audit_log(db, "IssueActivity", activity.issue_activity_id, action, changed_by=current_employee.employee_id)
   

@router.patch("/{id}/archive")
def archive_issue_activity(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    activity = db.query(models.IssueActivity).filter(models.IssueActivity.issue_activity_id == id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="IssueActivity not found")

    activity.entity_status = "ARCHIVED"
    activity.updated_at = now_utc()
    activity.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(activity)

    return {"message": "IssueActivity archived successfully", "activity_id": activity.issue_activity_id}
