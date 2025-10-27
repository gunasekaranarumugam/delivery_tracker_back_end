from fastapi import APIRouter, status, Depends
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.DeliverableRead, status_code=status.HTTP_201_CREATED)
def create_deliverable(payload: schemas.DeliverableCreate, db: Session = Depends(get_db)):
    deliverable = models.Deliverable(
        **payload.model_dump(exclude_unset=True),
        created_by="SYSTEM",
        updated_by="SYSTEM",
        created_at=datetime.utcnow()
    )
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)

    crud.audit_log(db, "Deliverable", deliverable.deliverable_id, "Create", changed_by="SYSTEM")
    return deliverable


@router.get("/", response_model=List[schemas.DeliverableRead])
def list_deliverables(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return db.query(models.Deliverable).offset(offset).limit(limit).all()



@router.get("/{id}", response_model=schemas.DeliverableRead)
def get_deliverable(id: str, db: Session = Depends(get_db)):
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
    return deliverable

@router.put("/{id}", response_model=schemas.DeliverableRead)
def update_deliverable(id: str, payload: schemas.DeliverableUpdate, db: Session = Depends(get_db)):
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()

    if not deliverable:
        # Create if not exists
        deliverable = models.Deliverable(
            deliverable_id=id,
            **payload.model_dump(exclude_unset=True),
            created_by="SYSTEM",
            updated_by="SYSTEM",
            created_at=datetime.utcnow()
        )
        db.add(deliverable)
    else:
        # Update existing
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(deliverable, key, value)
        deliverable.updatedat = datetime.utcnow()
        deliverable.updatedby = "SYSTEM"

    db.commit()
    db.refresh(deliverable)

    crud.audit_log(db, "Deliverable", deliverable.deliverable_id, "Update", changed_by="SYSTEM")
    return deliverable



@router.patch("/{id}/archive", response_model=schemas.DeliverableRead, status_code=status.HTTP_200_OK)
def patch_deliverable(
    id: str,
    payload: schemas.DeliverablePatch,  # schema with optional fields
    db: Session = Depends(get_db)
):
    # Fetch Deliverable
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
    
    if not deliverable:
        # Cannot patch a non-existent deliverable
        raise HTTPException(status_code=404, detail="Deliverable not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(deliverable, key, value)

    # Automatically archive if requested
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        deliverable.entity_status = "ARCHIVED"

    # Update timestamps and system info
    deliverable.updated_at = datetime.utcnow()
    deliverable.updated_by = "SYSTEM"

    db.commit()
    db.refresh(deliverable)

    # Audit log
    crud.audit_log(
        db,
        entity_type="Deliverable",
        entity_id=deliverable.deliverable_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return deliverable

