from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.TaskStatusRead, status_code=status.HTTP_201_CREATED, summary="Create a new Task Status")
def create_task_status(
    payload: schemas.TaskStatusCreate,
    db: Session = Depends(get_db),
    
):
    obj = models.TaskStatus(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "TaskStatus", obj.task_status_id, "Create",changed_by="system")
    return obj


@router.get("/", response_model=List[schemas.TaskStatusRead], summary="Get list of Task Statuses")
def list_task_statuses(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models.TaskStatus).filter(models.TaskStatus.entity_status != "ARCHIVED")
    return query.offset(offset).limit(limit).all()


@router.get("/{id}", response_model=schemas.TaskStatusRead, summary="Get Task Status by ID")
def get_task_status(id: str, db: Session = Depends(get_db)):
    obj = db.query(models.TaskStatus).filter(models.TaskStatus.task_status_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Task Status not found")
    return obj


@router.put("/{id}", response_model=schemas.TaskStatusRead, summary="Update Task Status")
def update_task_status(id: str, payload: schemas.TaskStatusCreate, db: Session = Depends(get_db)):
    obj = db.query(models.TaskStatus).filter(models.TaskStatus.task_status_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Task Status not found")

    for k, v in payload.model_dump().items():
        setattr(obj, k, v)

    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "TaskStatus", obj.task_status_id, "Update",changed_by="system")
    return obj





@router.patch("/{id}/archive", response_model=schemas.TaskStatusRead, status_code=status.HTTP_200_OK, summary="Archive Task Status")
def patch_task_status(
    id: str,
    payload: schemas.TaskStatusPatch,  # schema with optional fields
    db: Session = Depends(get_db)
):
    # Fetch TaskStatus
    task_status = db.query(models.TaskStatus).filter(models.TaskStatus.task_status_id == id).first()
    if not task_status:
        raise HTTPException(status_code=404, detail="Task Status not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task_status, key, value)

    # Automatically archive if entity_status is ARCHIVED
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        task_status.entity_status = "ARCHIVED"

    # Update timestamps and system info
    task_status.updated_at = datetime.utcnow()
    task_status.updated_by = "SYSTEM"

    db.commit()
    db.refresh(task_status)

    # Audit log
    crud.audit_log(
        db,
        entity_type="TaskStatus",
        entity_id=task_status.task_status_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return task_status

