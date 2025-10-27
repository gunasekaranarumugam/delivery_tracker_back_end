from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(
        **payload.model_dump(exclude_unset=True),
        created_by="SYSTEM",
        updated_by="SYSTEM",
        created_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    crud.audit_log(db, "Task", task.task_id, "Create", changed_by="SYSTEM")
    return task

@router.get("/", response_model=List[schemas.TaskRead])
def list_tasks(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return db.query(models.Task).offset(offset).limit(limit).all()



@router.get("/{id}", response_model=schemas.TaskRead)
def get_task(id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == id).first()
    return task


@router.put("/{id}", response_model=schemas.TaskRead)
def update_task(id: str, payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == id).first()

    if not task:
        # Create if not exists
        task = models.Task(
            task_id=id,
            **payload.model_dump(exclude_unset=True),
            created_by="SYSTEM",
            updated_by="SYSTEM",
            created_at=datetime.utcnow()
        )
        db.add(task)
    else:
        # Update existing
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        task.updatedat = datetime.utcnow()
        task.updatedby = "SYSTEM"

    db.commit()
    db.refresh(task)

    crud.audit_log(db, "Task", task.task_id, "Update", changed_by="SYSTEM")
    return task





@router.patch("/{id}/archive", response_model=schemas.TaskRead, status_code=status.HTTP_200_OK)
def patch_task(
    id: str,
    payload: schemas.TaskPatch,  # schema with all optional fields
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(models.Task.task_id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    # Automatically archive if entity_status=ARCHIVED
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        task.entity_status = "ARCHIVED"

    # Update audit info
    task.updated_at = datetime.utcnow()
    task.updated_by = "SYSTEM"

    db.commit()
    db.refresh(task)

    crud.audit_log(
        db,
        entity_type="Task",
        entity_id=task.task_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return task

