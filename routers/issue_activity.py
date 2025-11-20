from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=schemas.IssueActivityViewBase)
def create_issue_activity(
    payload: schemas.IssueActivityCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue_activity = models.IssueActivity(
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
                f"Failed to initialize Issue Activity model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(issue_activity)
        db.commit()
        db.refresh(issue_activity)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Issue Activity creation")
    try:
        crud.audit_log(
            db,
            "IssueActivity",
            issue_activity.issue_activity_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        issue_activity_view = (
            db.query(models.IssueActivityView)
            .filter(
                models.IssueActivityView.issue_activity_id
                == issue_activity.issue_activity_id
            )
            .first()
        )
        return issue_activity_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Issue Activity view.",
        )


@router.get("/", response_model=List[schemas.IssueActivityViewBase])
def list_issue_activities(db: Session = Depends(get_db)):
    try:
        issue_activity_view = (
            db.query(models.IssueActivityView)
            .filter(models.IssueActivityView.entity_status == "Active")
            .all()
        )
        return issue_activity_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issue Activity list.",
        )


@router.get("/{id}", response_model=schemas.IssueActivityViewBase)
def get_issue_activity(id: str, db: Session = Depends(get_db)):
    try:
        issue_activity_view = (
            db.query(models.IssueActivityView)
            .filter(models.IssueActivityView.issue_activity_id == id)
            .first()
        )
        if not issue_activity_view:
            raise HTTPException(status_code=404, detail="Issue Activity not found")
        return issue_activity_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Issue Activity details.",
        )


@router.put("/{id}", response_model=schemas.IssueActivityViewBase)
def update_issue_activity(
    id: str,
    payload: schemas.IssueActivityUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue_activity = (
            db.query(models.IssueActivity)
            .filter(models.IssueActivity.issue_activity_id == id)
            .first()
        )
        if not issue_activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue Activity not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issue Activity for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(issue_activity, key):
                continue
            setattr(issue_activity, key, value)
        issue_activity.updated_at = now_utc()
        issue_activity.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(issue_activity)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Issue Activity update")
    try:
        crud.audit_log(
            db,
            entity_type="IssueActivity",
            entity_id=issue_activity.issue_activity_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        issue_activity_view = (
            db.query(models.IssueActivityView)
            .filter(models.IssueActivityView.issue_activity_id == id)
            .first()
        )
        return issue_activity_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Issue Activity view after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.IssueActivityViewBase])
def archive_issue_activity(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        issue_activity = (
            db.query(models.IssueActivity)
            .filter(models.IssueActivity.issue_activity_id == id)
            .first()
        )
        if not issue_activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue Activity not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Issue Activity for update.",
        )
    try:
        issue_activity.entity_status = "Archived"
        issue_activity.updated_at = now_utc()
        issue_activity.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(issue_activity)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Issue Activity update")
    try:
        crud.audit_log(
            db,
            entity_type="IssueActivity",
            entity_id=issue_activity.issue_activity_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        issue_activity_view = (
            db.query(models.IssueActivityView)
            .filter(models.IssueActivityView.entity_status == "Active")
            .all()
        )
        return issue_activity_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Issue Activity view after update.",
        )
