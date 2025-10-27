from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.TaskTypeMasterRead, status_code=201)
def create_task_type(payload: schemas.TaskTypeMasterCreate, db: Session = Depends(get_db)):
    obj = models.TaskTypeMaster(
        task_type_id=payload.task_type_id,
        task_type_Name=payload.task_type_Name,
        task_type_description=payload.task_type_description,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "TaskTypeMaster", obj.task_type_id, "Create", changed_by="system")
    return obj



@router.get("/", response_model=List[schemas.TaskTypeMasterRead], summary="Get list of Task Type records")
def list_task_types(limit: int = Query(100, ge=1), offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models.TaskTypeMaster).filter(models.TaskTypeMaster.entity_status != "ARCHIVED")
    return query.offset(offset).limit(limit).all()



@router.get("/{id}", response_model=schemas.TaskTypeMasterRead, summary="Get Task Type by ID")
def get_task_type(id: str, db: Session = Depends(get_db)):
    obj = db.query(models.TaskTypeMaster).filter(models.TaskTypeMaster.task_type_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Task Type not found")
    return obj



@router.put("/{id}", response_model=schemas.TaskTypeMasterRead, summary="Update Task Type record")
def update_task_type(id: str, payload: schemas.TaskTypeMasterCreate, db: Session = Depends(get_db)):
    obj = db.query(models.TaskTypeMaster).filter(models.TaskTypeMaster.task_type_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Task Type not found")

    for k, v in payload.model_dump().items():
        setattr(obj, k, v)

    obj.updated_at = datetime.utcnow()
    obj.updated_by = ""  # no auth
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "TaskTypeMaster", obj.task_type_id, "Update", changed_by="system")
    return obj



@router.patch("/{id}/archive", response_model=schemas.TaskTypeMasterRead, status_code=status.HTTP_200_OK, summary="Archive Task Type record")
def patch_task_type(
    id: str,
    payload: schemas.TaskTypeMasterPatch,  # Schema with optional fields
    db: Session = Depends(get_db)
):
    # Fetch TaskType
    task_type = db.query(models.TaskTypeMaster).filter(models.TaskTypeMaster.task_type_id == id).first()
    if not task_type:
        raise HTTPException(status_code=404, detail="Task Type not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task_type, key, value)

    # Automatically handle archiving if requested
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        task_type.entity_status = "ARCHIVED"

    # Update timestamps and system info
    task_type.updated_at = datetime.utcnow()
    task_type.updated_by = "SYSTEM"

    db.commit()
    db.refresh(task_type)

    # Audit log
    crud.audit_log(
        db,
        entity_type="TaskTypeMaster",
        entity_id=task_type.task_type_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return task_type

