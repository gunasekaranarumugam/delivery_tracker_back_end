from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db
from .deliverable import get_current_user_from_cookie

router = APIRouter()


@router.post("/", response_model=schemas.MilestoneRead, summary="Add new Milestone")
def create_milestone(
    payload: schemas.MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Permission: only BU_HEAD or PROJECT_MANAGER can create
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to create milestones")

    # Check if MilestoneId exists
    existing = db.query(models.Milestone).filter(models.Milestone.MilestoneId == payload.MilestoneId).first()
    if existing:
        raise HTTPException(status_code=400, detail="MilestoneId already exists")

    # Validate ProjectId exists
    project = db.query(models.Project).filter(models.Project.ProjectId == payload.ProjectId).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # PROJECT_MANAGERs restricted to their BU only
    if current_user.role_name == models.Role.PROJECT_MANAGER:
        if not current_user.BUId or project.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Cannot create milestones outside your Business Unit")

    milestone = models.Milestone(**payload.dict())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    crud.audit_log(db, "Milestone", milestone.MilestoneId, "Create")
    return milestone


@router.get("/", response_model=List[schemas.MilestoneRead], summary="List milestones")
def list_milestones(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    query = db.query(models.Milestone).join(models.Project).filter(models.Milestone.EntityStatus != "Archived")

    forbidden_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.DELIVERY_MANAGER]
    if current_user.role_name in forbidden_roles:
        raise HTTPException(status_code=403, detail="Can't view milestones details")

    # BU_HEAD can see all their BU milestones, PROJECT_MANAGER limited by BU
    if current_user.role_name == models.Role.PROJECT_MANAGER:
        query = query.filter(models.Project.BUId == current_user.BUId)
    elif current_user.role_name == models.Role.BU_HEAD:
        query = query.filter(models.Project.BUId == current_user.BUId)
    else:
        # Other roles restricted to their BU
        query = query.filter(models.Project.BUId == current_user.BUId)

    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.MilestoneRead, summary="Get milestone by ID")
def get_milestone(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    milestone = db.query(models.Milestone).filter(models.Milestone.MilestoneId == item_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    # Permission check: non BU_HEAD can see only if BU matches
    project = db.query(models.Project).filter(models.Project.ProjectId == milestone.ProjectId).first()
    if current_user.role_name != models.Role.BU_HEAD and project.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Not authorized to view this milestone")

    return milestone


@router.put("/{item_id}", response_model=schemas.MilestoneRead, summary="Update Milestone")
def update_milestone(
    item_id: str,
    payload: schemas.MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to update milestones")

    milestone = db.query(models.Milestone).filter(models.Milestone.MilestoneId == item_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = db.query(models.Project).filter(models.Project.ProjectId == milestone.ProjectId).first()
    if current_user.role_name == models.Role.PROJECT_MANAGER and project.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update milestones outside your Business Unit")

    for k, v in payload.dict().items():
        setattr(milestone, k, v)
    milestone.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(milestone)

    crud.audit_log(db, "Milestone", milestone.MilestoneId, "Update", changed_by=current_user.userName)
    return milestone


@router.patch("/{item_id}/archive", summary="Archive Milestone")
def archive_milestone(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to archive milestones")

    milestone = db.query(models.Milestone).filter(models.Milestone.MilestoneId == item_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = db.query(models.Project).filter(models.Project.ProjectId == milestone.ProjectId).first()
    if current_user.role_name == models.Role.PROJECT_MANAGER and project.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot archive milestones outside your Business Unit")

    milestone.EntityStatus = "Archived"
    milestone.UpdatedAt = datetime.utcnow()
    db.commit()

    crud.audit_log(db, "Milestone", milestone.MilestoneId, "Archive", changed_by=current_user.userName)
    return {"status": "archived"}
