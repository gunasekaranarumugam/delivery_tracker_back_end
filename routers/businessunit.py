from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


def now():
    return datetime.utcnow()

@router.post("/", response_model=schemas.BusinessUnitRead, status_code=status.HTTP_201_CREATED)
def create_business_unit(payload: schemas.BusinessUnitCreate, db: Session = Depends(get_db)):
    bu = models.BusinessUnit(
        business_unit_id=payload.business_unit_id,
        business_unit_name=payload.business_unit_name,
        business_unit_head_id=payload.business_unit_head_id,
        business_unit_description=payload.business_unit_description,
        created_at=now(),
        updated_at=now(),
        created_by="SYSTEM",
        updated_by="SYSTEM",
        entity_status="Active"
    )

    db.add(bu)
    db.commit()
    db.refresh(bu)

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=bu.business_unit_id,
        action="Create",
        changed_by="SYSTEM"
    )
    return bu

#@router.get("/", response_model=List[schemas.BusinessUnitRead])
#def list_business_units(db: Session = Depends(get_db)):
#    return db.query(models.BusinessUnit).all()

@router.get("/", response_model=List[schemas.BusinessUnitRead])
def list_business_units(db: Session = Depends(get_db)):
    # Add filtering here to exclude 'ARCHIVED' records
    return db.query(models.BusinessUnit).filter(
        models.BusinessUnit.entity_status == "Active"
    ).all()

    


@router.get("/{id}", response_model=schemas.BusinessUnitRead)
def get_business_unit(id: str, db: Session = Depends(get_db)):
    bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.business_unit_id == id).first()
    if not bu:
        raise HTTPException(status_code=404, detail="Business Unit not found")
    return bu


@router.put("/{id}", response_model=schemas.BusinessUnitRead)
def update_business_unit(id: str, payload: schemas.BusinessUnitCreate, db: Session = Depends(get_db)):
    bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.business_unit_id == id).first()
    if not bu:
        # Create if not exists
        bu = models.BusinessUnit(
            business_unit_id=id,
            business_unit_name=payload.business_unit_name or "Unnamed BU",
            business_unit_head_id=payload.business_unit_head_id or "SYSTEM",
            business_unit_description=payload.business_unit_description or "No description",
            created_at=now(),
            updated_at=now(),
            created_by="SYSTEM",
            updated_by="SYSTEM",
            entity_status="Active"
        )
        db.add(bu)
    else:
        # Update existing
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(bu, key, value)
        bu.updated_at = now()
        bu.updated_by = "SYSTEM"
        if not bu.business_unit_head_id:
            bu.business_unit_head_id = "SYSTEM"
        if not bu.business_unit_description:
            bu.business_unit_description = "No description"

    db.commit()
    db.refresh(bu)

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=bu.business_unit_id,
        action="Update",
        changed_by="SYSTEM"
    )
    return bu


@router.patch("/{id}/archive", response_model=schemas.BusinessUnitRead, status_code=status.HTTP_200_OK)
def patch_business_unit(
    id: str,
    payload: schemas.BusinessUnitPatch,  # schema with optional fields
    db: Session = Depends(get_db)
):
    # Fetch Business Unit
    bu = db.query(models.BusinessUnit).filter(models.BusinessUnit.business_unit_id == id).first()
    
    if not bu:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(bu, key, value)

    # Automatically archive if requested
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        bu.entity_status = "ARCHIVED"

    # Update timestamps and system info
    bu.updated_at = datetime.utcnow()
    bu.updated_by = "SYSTEM"

    db.commit()
    db.refresh(bu)

    # Audit log
    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=bu.business_unit_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return bu
