from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db
from .deliverable import get_current_user_from_cookie

router = APIRouter()


@router.post("/", response_model=schemas.IssueActivityRead, summary="Add new Issue Activity")
def create_issue_activity(
    payload: schemas.IssueActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    allowed_roles = [
        models.Role.PROJECT_MANAGER,
        models.Role.DELIVERY_MANAGER,
        models.Role.TEAM_MEMBER,
        models.Role.ADMIN,
    ]
    if current_user.role_name not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to create issue activity")

    existing = db.query(models.IssueActivity).filter(models.IssueActivity.IssueActivityId == payload.IssueActivityId).first()
    if existing:
        raise HTTPException(status_code=400, detail="IssueActivityId already exists")

    issue = db.query(models.Issue).filter(models.Issue.IssueId == payload.IssueId).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == issue.DeliverableId).first()
    # PROJECT_MANAGER can only create inside their BU
    if current_user.role_name == models.Role.PROJECT_MANAGER and deliverable.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot create issue activities outside your Business Unit")

    issue_activity = models.IssueActivity(**payload.dict())
    db.add(issue_activity)
    db.commit()
    db.refresh(issue_activity)

    crud.audit_log(db, "IssueActivity", issue_activity.IssueActivityId, "Create", changed_by=current_user.userName)
    return issue_activity


@router.get("/", response_model=List[schemas.IssueActivityRead], summary="List Issue Activities")
def list_issue_activities(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    query = db.query(models.IssueActivity).join(models.Issue).join(models.Deliverable)

    # Roles forbidden to view
    forbidden_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.DELIVERY_MANAGER]
    if current_user.role_name in forbidden_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

    if current_user.role_name == models.Role.ADMIN:
        # Admin sees all
        pass
    elif current_user.role_name in [models.Role.PROJECT_MANAGER, models.Role.BU_HEAD]:
        # PM and BU_HEAD see only their BU
        query = query.filter(models.Deliverable.BUId == current_user.BUId)
    else:
        # Other roles forbidden by default
        raise HTTPException(status_code=403, detail="Can't view details")

    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.IssueActivityRead, summary="Get Issue Activity by ID")
def get_issue_activity(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.IssueActivity).filter(models.IssueActivity.IssueActivityId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="IssueActivity not found")

    issue = db.query(models.Issue).filter(models.Issue.IssueId == obj.IssueId).first()
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == issue.DeliverableId).first()

    # Only allow BU_HEAD and ADMIN full access, others limited to their BU
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.ADMIN] and deliverable.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Not authorized to view this issue activity")

    return obj


@router.put("/{item_id}", response_model=schemas.IssueActivityRead, summary="Update Issue Activity")
def update_issue_activity(
    item_id: str,
    payload: schemas.IssueActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    allowed_roles = [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]
    if current_user.role_name not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to update issue activities")

    obj = db.query(models.IssueActivity).filter(models.IssueActivity.IssueActivityId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="IssueActivity not found")

    issue = db.query(models.Issue).filter(models.Issue.IssueId == obj.IssueId).first()
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.DeliverableId == issue.DeliverableId).first()

    if current_user.role_name == models.Role.PROJECT_MANAGER and deliverable.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update issue activities outside your Business Unit")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    obj.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "IssueActivity", obj.IssueActivityId, "Update", changed_by=current_user.userName)
    return obj


@router.patch("/{item_id}/archive", summary="Archive Issue Activity (not implemented)")
def archive_issue_activity(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Implement archiving logic here (soft delete or status flag)
    raise HTTPException(status_code=501, detail="Archive endpoint not implemented for IssueActivity")
