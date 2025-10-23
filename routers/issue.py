from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db
from .deliverable import get_current_user_from_cookie

router = APIRouter()


@router.post("/", response_model=schemas.IssueRead, summary="Add new Issue")
def create_issue(
    payload: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only BU_HEAD and PROJECT_MANAGER can create issues
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to create issues")

    # Check if IssueId already exists
    existing = db.query(models.Issue).filter(models.Issue.IssueId == payload.IssueId).first()
    if existing:
        raise HTTPException(status_code=400, detail="IssueId already exists")

    # Validate Deliverable exists
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == payload.DeliverableId).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    # Validate ActionOwnerId (Employee) if provided
    if payload.ActionOwnerId:
        employee = db.query(models.Employee).filter(models.Employee.EmployeeId == payload.ActionOwnerId).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Action owner employee not found")

    # PROJECT_MANAGER BU restriction
    if current_user.role_name == models.Role.PROJECT_MANAGER and deliverable.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot create issues outside your Business Unit")

    issue = models.Issue(**payload.dict())
    db.add(issue)
    db.commit()
    db.refresh(issue)

    crud.audit_log(db, "Issue", issue.IssueId, "Create", changed_by=current_user.userName)
    return issue


@router.get("/", response_model=List[schemas.IssueRead], summary="List Issues")
def list_issues(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    query = db.query(models.Issue).join(models.Deliverable).filter(models.Issue.EntityStatus != "Archived")

    # Roles that can't view the list
    forbidden_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.DELIVERY_MANAGER]
    if current_user.role_name in forbidden_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

    if current_user.role_name == models.Role.PROJECT_MANAGER:
        query = query.filter(models.Deliverable.BUId == current_user.BUId)
    elif current_user.role_name == models.Role.BU_HEAD:
        # BU_HEAD sees their BU only
        query = query.filter(models.Deliverable.BUId == current_user.BUId)
    else:
        # Other roles forbidden
        raise HTTPException(status_code=403, detail="Can't view details")

    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.IssueRead, summary="Get Issue by ID")
def get_issue(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    issue = db.query(models.Issue).filter(models.Issue.IssueId == item_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Restrict access based on BU if not BU_HEAD
    if current_user.role_name != models.Role.BU_HEAD:
        deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == issue.DeliverableId).first()
        if deliverable.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Not authorized to view this issue")

    return issue


@router.put("/{item_id}", response_model=schemas.IssueRead, summary="Update Issue")
def update_issue(
    item_id: str,
    payload: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only BU_HEAD and PROJECT_MANAGER can update
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to update issues")

    issue = db.query(models.Issue).filter(models.Issue.IssueId == item_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == issue.DeliverableId).first()

    # PROJECT_MANAGER BU restriction on update
    if current_user.role_name == models.Role.PROJECT_MANAGER and deliverable.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update issues outside your Business Unit")

    for k, v in payload.dict().items():
        setattr(issue, k, v)
    issue.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(issue)

    crud.audit_log(db, "Issue", issue.IssueId, "Update", changed_by=current_user.userName)
    return issue


@router.patch("/{item_id}/archive", summary="Archive Issue")
def archive_issue(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only BU_HEAD and PROJECT_MANAGER can archive
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to archive issues")

    issue = db.query(models.Issue).filter(models.Issue.IssueId == item_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == issue.DeliverableId).first()

    # PROJECT_MANAGER BU restriction on archive
    if current_user.role_name == models.Role.PROJECT_MANAGER and deliverable.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot archive issues outside your Business Unit")

    issue.EntityStatus = "Archived"
    issue.UpdatedAt = datetime.utcnow()
    db.commit()

    crud.audit_log(db, "Issue", issue.IssueId, "Archive", changed_by=current_user.userName)
    return {"status": "archived"}
