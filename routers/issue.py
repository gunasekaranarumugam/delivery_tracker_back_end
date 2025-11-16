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


@router.post("/", response_model=schemas.IssueRead, status_code=status.HTTP_201_CREATED)
def create_issue(
    payload: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue = models.Issue(
            **payload.model_dump(exclude_unset=True),
            created_by=current_employee.employee_id,
            updated_by=current_employee.employee_id,
            created_at=now_utc(),
            updated_at=now_utc(),
            entity_status="Active",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize Issue model.",
        )

    try:
        db.add(issue)
        db.commit()
        db.refresh(issue)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Issue creation")
    except Exception as e:
        handle_db_error(db, e, "Issue creation (unexpected)")

    try:
        issue_view = (
            db.query(models.IssueView)
            .filter(models.IssueView.issue_id == issue.issue_id)
            .first()
        )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying issue view after creation.",
        )

    crud.audit_log(
        db, "Issue", issue.issue_id, "Create", changed_by=current_employee.employee_id
    )
    return issue_view if issue_view else issue


@router.get("/", response_model=List[schemas.IssueRead])
def list_issues(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    try:
        return (
            db.query(models.IssueView)
            .filter(models.IssueView.entity_status != "ARCHIVED")
            .all()
        )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issues list.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while listing Issues.",
        )


@router.get("/{id}", response_model=schemas.IssueRead)
def get_issue(id: str, db: Session = Depends(get_db)):
    try:
        issue = (
            db.query(models.IssueView).filter(models.IssueView.issue_id == id).first()
        )

        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
            )
        return issue

    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching single Issue.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching Issue.",
        )


@router.put("/{id}", response_model=schemas.IssueRead)
def update_issue(
    id: str,
    payload: schemas.IssueUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    action = "Update"

    try:
        issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving Issue for update.",
        )

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
                entity_status="Active",
            )
            db.add(issue)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize new Issue model.",
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
                detail=f"Failed to apply update payload: {e}",
            )

    try:
        db.commit()
        db.refresh(issue)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, f"Issue {action.lower()}")
    except Exception as e:
        handle_db_error(db, e, f"Issue {action.lower()} (unexpected)")

    crud.audit_log(
        db, "Issue", issue.issue_id, action, changed_by=current_employee.employee_id
    )

    try:
        issue_view = (
            db.query(models.IssueView)
            .filter(models.IssueView.issue_id == issue.issue_id)
            .first()
        )
        return issue_view or issue
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Issue view after update.",
        )


@router.patch("/{id}/archive")
def archive_issue(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.entity_status = "ARCHIVED"
    issue.updated_at = now_utc()
    issue.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(issue)

    return {"message": "Issue archived successfully", "issue_id": issue.issue_id}
