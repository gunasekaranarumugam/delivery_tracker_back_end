from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=List[schemas.IssueViewBase])
def create_issue(
    payload: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue = models.Issue(
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
                f"Failed to initialize Issue model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(issue)
        db.commit()
        db.refresh(issue)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Issue creation")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Issue creation (unexpected)")
    try:
        crud.audit_log(
            db,
            "Issue",
            issue.issue_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        issue_view = (
            db.query(models.IssueView)
            .filter(models.IssueView.entity_status == "Active")
            .all()
        )
        return issue_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Issue view.",
        )


@router.get("/", response_model=List[schemas.IssueViewBase])
def list_issues(db: Session = Depends(get_db)):
    try:
        issue_view = (
            db.query(models.IssueView)
            .filter(models.IssueView.entity_status == "Active")
            .all()
        )
        return issue_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issue list.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing Issue: {e}",
        )


@router.get("/{id}", response_model=schemas.IssueViewBase)
def get_issue(id: str, db: Session = Depends(get_db)):
    try:
        issue_view = (
            db.query(models.IssueView).filter(models.IssueView.issue_id == id).first()
        )
        if not issue_view:
            raise HTTPException(status_code=404, detail="Issue not found")
        return issue_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Issue details.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching Issue details: {e}",
        )


@router.put("/{id}", response_model=schemas.IssueViewBase)
def update_issue(
    id: str,
    payload: schemas.IssueUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issue for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(issue, key):
                continue
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
        db.rollback()
        handle_db_error(db, e, "Issue update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Issue update (unexpected)")
    try:
        crud.audit_log(
            db,
            entity_type="Issue",
            entity_id=issue.issue_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        issue_view = (
            db.query(models.IssueView).filter(models.IssueView.issue_id == id).first()
        )
        return issue_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Issue view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.IssueViewBase])
def archive_issue(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issue for update.",
        )
    try:
        issue.entity_status = "Archived"
        issue.updated_at = now_utc()
        issue.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Issue update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Issue update (unexpected)")
    try:
        db.commit()
        db.refresh(issue)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Issue update")
    except Exception as e:
        db.rollback()
        handle_db_error(db, e, "Issue update (unexpected)")

    try:
        crud.audit_log(
            db,
            entity_type="Issue",
            entity_id=issue.issue_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        issue_view = (
            db.query(models.IssueView)
            .filter(models.IssueView.entity_status == "Active")
            .all()
        )
        return issue_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Issue view after update.",
        )
