from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.IssueRead, status_code=status.HTTP_201_CREATED)
def create_issue(payload: schemas.IssueCreate, db: Session = Depends(get_db)):
    issue = models.Issue(
        **payload.model_dump(exclude_unset=True),
        created_by="SYSTEM",
        updated_by="SYSTEM",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
     
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    crud.audit_log(db, "Issue", issue.issue_id, "Create", changed_by="SYSTEM")
    return issue


@router.get("/", response_model=List[schemas.IssueRead])
def list_issues(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
     return (
        db.query(models.Issue)
        .filter(models.Issue.entity_status == 'Active') # ✅ THE CRUCIAL FILTER
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{id}", response_model=schemas.IssueRead)
def get_issue(id: str, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
    return issue


@router.put("/{id}", response_model=schemas.IssueRead)
def update_issue(id: str, payload: schemas.IssueCreate, db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()

    if not issue:
        # Create if not exists
        issue = models.Issue(
            issue_id=id,
            **payload.model_dump(exclude_unset=True),
            created_by="SYSTEM",
            updated_by="SYSTEM",
            created_at=datetime.utcnow()
        )
        db.add(issue)
    else:
        # Update existing
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(issue, key, value)
        issue.updated_at = datetime.utcnow()
        issue.updated_by = "SYSTEM"

    db.commit()
    db.refresh(issue)

    crud.audit_log(db, "Issue", issue.issue_id, "Update", changed_by="SYSTEM")
    return issue


@router.patch("/{id}/archive", response_model=schemas.IssueRead, status_code=status.HTTP_200_OK)
def patch_issue(
    id: str,
    payload: schemas.IssuePatch,  # schema with optional fields
    db: Session = Depends(get_db)
):
    # Fetch Issue
    issue = db.query(models.Issue).filter(models.Issue.issue_id == id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Update only the fields provided in the payload
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(issue, key, value)

    # Automatically archive if entity_status is ARCHIVED
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        issue.entity_status = "ARCHIVED"

    # Update timestamps and system info
    issue.updated_at = datetime.utcnow()
    issue.updated_by = "SYSTEM"

    db.commit()
    db.refresh(issue)

    # Audit log
    crud.audit_log(
        db,
        entity_type="Issue",
        entity_id=issue.issue_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return issue

