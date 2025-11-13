from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
from datetime import datetime, timezone
from main import models, schemas, crud
from main.database import get_db
from .employee import get_current_employee
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
# --- POST / (Create Issue) ---
# ----------------------------------------------------------------------
@router.post("/", response_model=schemas.IssueRead, status_code=status.HTTP_201_CREATED)
def create_issue(payload: schemas.IssueCreate, db: Session = Depends(get_db),current_employee: models.Employee = Depends(get_current_employee)):
    try:
        issue = models.Issue(
            **payload.model_dump(exclude_unset=True),
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_at=now_utc(),
            entity_status="Active"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize Issue model.")

    # Commit and refresh
    try:
        db.add(issue)
        db.commit()
        db.refresh(issue)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Issue creation")
    except Exception as e:
        handle_db_error(db, e, "Issue creation (unexpected)")

    # Retrieve view for full response data
    try:
        issue_view = db.query(models.IssueView).filter(models.IssueView.issue_id == issue.issue_id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while querying issue view after creation.")

    crud.audit_log(db, "Issue", issue.issue_id, "Create", changed_by=current_employee.employee_id)
    return issue_view if issue_view else issue


# ----------------------------------------------------------------------
# --- GET / (List Issues) ---
# ----------------------------------------------------------------------
@router.get("/", response_model=List[schemas.IssueRead])
def list_issues(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        # Filter to exclude 'ARCHIVED' records and apply limit/offset
        return db.query(models.IssueView).filter(
            models.IssueView.entity_status != "ARCHIVED"
        ).all()
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching Issues list.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while listing Issues.")


# ----------------------------------------------------------------------
# --- GET /{id} (Get Single Issue) ---
# ----------------------------------------------------------------------
@router.get("/{id}", response_model=schemas.IssueRead)
def get_issue(id: str, db: Session = Depends(get_db)):
    try:
        # Query the View model for full joined data
        issue = db.query(models.IssueView).filter(models.IssueView.issue_id == id).first()
        
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return issue
        
    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching single Issue.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while fetching Issue.")


# ----------------------------------------------------------------------
# --- PUT /{id} (Update or Create Issue) ---
# ----------------------------------------------------------------------
@router.put("/{id}", response_model=schemas.IssueRead)
def update_issue(id: str, payload: schemas.IssueUpdate, db: Session = Depends(get_db),current_employee: models.Employee = Depends(get_current_employee)):
    action = "Update"
    
    # 1. Retrieve existing issue
    try:
        issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Issue for update."
        )

    # 2. Conditional Create or Update
    if not issue:
        action = "Create"
        try:
            issue = models.Issue(
                issue_id=id,
                **payload.model_dump(exclude_unset=True),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=now_utc(),
                updated_at=now_utc(),
                entity_status="Active"
            )
            db.add(issue)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize new Issue model."
            )
    else:
        try:
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(issue, key, value)
            issue.updated_at = now_utc()
            issue.updated_by = current_employee.employee_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply update payload: {e}"
            )

    # 3. Commit and refresh
    try:
        db.commit()
        db.refresh(issue)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, f"Issue {action.lower()}")
    except Exception as e:
        handle_db_error(db, e, f"Issue {action.lower()} (unexpected)")

    # 4. Audit log
    crud.audit_log(db, "Issue", issue.issue_id, action, changed_by=current_employee.employee_id)
    
    # 5. Return the full view data
    try:
        issue_view = db.query(models.IssueView).filter(models.IssueView.issue_id == issue.issue_id).first()
        return issue_view or issue
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Issue view after update."
        )


@router.patch("/{id}/archive")
def archive_issue(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee)
):
    # Fetch Issue
    issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Soft delete / archive
    issue.entity_status = "ARCHIVED"
    issue.updated_at = now_utc()
    issue.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(issue)

    return {"message": "Issue archived successfully", "issue_id": issue.issue_id}

