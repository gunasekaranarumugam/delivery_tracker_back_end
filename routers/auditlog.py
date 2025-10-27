from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.AuditLogRead, summary="Create a new Audit Log record")
def create_audit_log(payload: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    obj = models.AuditLog(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj



@router.get("/", response_model=List[schemas.AuditLogRead], summary="Get all Audit Log records")
def list_audit_logs(limit: int = Query(100, ge=1), offset: int = 0, db: Session = Depends(get_db)):
    return db.query(models.AuditLog).offset(offset).limit(limit).all()


@router.get("/{id}", response_model=schemas.AuditLogRead, summary="Get Audit Log by ID")
def get_audit_log(id: str, db: Session = Depends(get_db)):
    return db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()



@router.put("/{id}", response_model=schemas.AuditLogRead, summary="Update Audit Log record")
def update_audit_log(id: str, payload: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    obj = db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{id}/archive", response_model=schemas.AuditLogRead, summary="Partially update Audit Log")
def patch_audit_log(id: str, payload: schemas.AuditLogPatch, db: Session = Depends(get_db)):
    obj = db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj



