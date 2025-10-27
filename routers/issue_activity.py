from fastapi import APIRouter, status, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.IssueActivityRead, status_code=status.HTTP_201_CREATED)
def create_issue_activity(payload: schemas.IssueActivityCreate, db: Session = Depends(get_db)):
    activity = models.IssueActivity(
        **payload.model_dump(exclude_unset=True),
        created_by="SYSTEM",
        updated_by="SYSTEM",
        created_at=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    crud.audit_log(db, "IssueActivity", activity.issue_activity_id, "Create", changed_by="SYSTEM")
    return activity


@router.get("/", response_model=List[schemas.IssueActivityRead])
def list_issue_activities(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return db.query(models.IssueActivity).offset(offset).limit(limit).all()


@router.get("/{id}", response_model=schemas.IssueActivityRead)
def get_issue_activity(id: str, db: Session = Depends(get_db)):
    return db.query(models.IssueActivity).filter(models.IssueActivity.issue_activity_id == id).first()


@router.put("/{id}", response_model=schemas.IssueActivityRead)
def update_issue_activity(id: str, payload: schemas.IssueActivityCreate, db: Session = Depends(get_db)):
    activity = db.query(models.IssueActivity).filter(models.IssueActivity.issue_activity_id == id).first()

    if not activity:
        # Create if not exists
        activity = models.IssueActivity(
            issue_activity_id=id,
            **payload.model_dump(exclude_unset=True),
            created_by="SYSTEM",
            updated_by="SYSTEM",
            created_at=datetime.utcnow()
        )
        db.add(activity)
    else:
        # Update existing
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(activity, key, value)
        activity.updatedat = datetime.utcnow()
        activity.updatedby = "SYSTEM"

    db.commit()
    db.refresh(activity)

    crud.audit_log(db, "IssueActivity", activity.issue_activity_id, "Update", changed_by="SYSTEM")
    return activity
    

@router.patch("/{id}/archive", response_model=schemas.IssueActivityRead, status_code=status.HTTP_200_OK)
def patch_issue_activity(
    id: str,
    payload: schemas.IssueActivityPatch,  # schema with optional fields
    db: Session = Depends(get_db)
):
    # Fetch Issue Activity
    activity = db.query(models.IssueActivity).filter(models.IssueActivity.issue_activity_id == id).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Issue Activity not found")

    # Update only the fields provided
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, key, value)

    # Automatically archive if entity_status is ARCHIVED
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        activity.entity_status = "ARCHIVED"

    # Update timestamps and system info
    activity.updated_at = datetime.utcnow()
    activity.updated_by = "SYSTEM"

    db.commit()
    db.refresh(activity)

    # Audit log
    crud.audit_log(
        db,
        entity_type="IssueActivity",
        entity_id=activity.issue_activity_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return activity

