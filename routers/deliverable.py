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



# --- 2. DEDICATED ARCHIVE ENDPOINT ---
# The logic that should be under the /archive path.
@router.patch("/{id}/archive", response_model=schemas.DeliverableRead, status_code=status.HTTP_200_OK)
def archive_deliverable(
    id: str,
    db: Session = Depends(get_db),
    
):
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
    
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
        
    if deliverable.entity_status == "ARCHIVED":
        # THIS IS LIKELY THE CAUSE OF THE 422 ERROR IN YOUR SCENARIO
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="Deliverable is already archived."
        )

    # Enforce the archival action directly
    deliverable.entity_status = "ARCHIVED"

    # Update metadata
    deliverable.updated_at = datetime.utcnow()
    deliverable.updated_by = "SYSTEM"

    db.commit()
    db.refresh(deliverable)
    
    # Audit log logic...
    
    return deliverable

