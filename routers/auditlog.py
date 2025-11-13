from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

# Helper function to handle common DB exceptions (reused logic)
def handle_db_error(db: Session, e: Exception, operation: str):
    # Only rollback if the session is still active/open
    try:
        db.rollback()
    except Exception:
        pass # Ignore errors on rollback itself
        
    # Handle IntegrityError (e.g., duplicate key)
    if isinstance(e, IntegrityError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{operation} failed due to a data constraint violation."
        )
    # Handle OperationalError (e.g., table doesn't exist, bad syntax)
    if isinstance(e, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: Database operational error. Check the SQL syntax or connection."
        )
    # Handle other general database API errors
    elif isinstance(e, DBAPIError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation} failed: A database connection or query execution error occurred."
        )
    # Catch-all for unexpected errors
    else:
        # Log the unexpected error for debugging purposes if possible
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during the {operation} operation."
        )

# ----------------------------------------------------------------------
# --- POST / (Create Audit Log) ---
# ----------------------------------------------------------------------
@router.post("/", response_model=schemas.AuditLogRead, summary="Create a new Audit Log record", status_code=status.HTTP_201_CREATED)
def create_audit_log(payload: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    try:
        # Instantiate the model
        obj = models.AuditLog(**payload.model_dump(exclude_unset=True))
        
        # Add, commit, and refresh
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
        
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Audit Log creation")
    except Exception as e:
        handle_db_error(db, e, "Audit Log creation (unexpected)")


# ----------------------------------------------------------------------
# --- GET / (List Audit Log records) ---
# ----------------------------------------------------------------------
@router.get("/", response_model=List[schemas.AuditLogRead], summary="Get all Audit Log records")
def list_audit_logs(limit: int = Query(100, ge=1), offset: int = 0, db: Session = Depends(get_db)):
    try:
        # Apply limit and offset directly to the query
        return db.query(models.AuditLog).limit(limit).offset(offset).all()
        
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching Audit Logs.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while listing Audit Logs.")


# ----------------------------------------------------------------------
# --- GET /{id} (Get Audit Log by ID) ---
# ----------------------------------------------------------------------
@router.get("/{id}", response_model=schemas.AuditLogRead, summary="Get Audit Log by ID")
def get_audit_log(id: str, db: Session = Depends(get_db)):
    try:
        obj = db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit Log record not found")
        return obj
    
    except HTTPException as e:
        raise e
    except (DBAPIError, OperationalError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching Audit Log by ID.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while fetching Audit Log.")


# ----------------------------------------------------------------------
# --- PUT /{id} (Update Audit Log record) ---
# ----------------------------------------------------------------------
@router.put("/{id}", response_model=schemas.AuditLogRead, summary="Update Audit Log record")
def update_audit_log(id: str, payload: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    # 1. Retrieve the existing object
    try:
        obj = db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit Log record not found")
    except (DBAPIError, OperationalError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while retrieving Audit Log for update.")

    # 2. Apply updates
    try:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to apply update payload: {e}")

    # 3. Commit
    try:
        db.commit()
        db.refresh(obj)
        return obj
        
    except (IntegrityError, DBAPIError, OperationalError) as e:
        handle_db_error(db, e, "Audit Log update")
    except Exception as e:
        handle_db_error(db, e, "Audit Log update (unexpected)")


