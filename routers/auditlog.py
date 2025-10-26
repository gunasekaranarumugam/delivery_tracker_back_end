from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"


# Utility to get current user from cookie
def get_current_user_from_cookie(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db),
    # Note: token from header is usually preferred over cookie if both exist, 
    # but the original logic only uses the cookie 'access_token'.
    token: Optional[str] = Depends(oauth2_scheme), 
) -> models.User:
    # Use access_token from cookie as the primary source
    if not access_token:
        # Fallback to Authorization header if cookie is missing
        if token:
            access_token = token
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        # The 'sub' should contain the full_name
        full_name = payload.get("sub") 
        if not full_name:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # FIX: Use correct user field: models.User.full_name
    # Assuming 'role' is a relationship on models.User
    user = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.full_name == full_name).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ------------------------- AUDIT LOG ENDPOINTS -------------------------

# ✅ CREATE Audit Log (Admin only)
@router.post("/", response_model=schemas.AuditLogRead, summary="Add new Audit Log record.")
def create_audit_log(
    payload: schemas.AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Permission Check
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can create audit logs.")

    # Check for existing ID if provided in payload (though Audit ID should ideally be auto-generated)
    # FIX: Use the correct field name: audit_id
    if hasattr(payload, 'audit_id'):
        existing_log = db.query(models.AuditLog).filter(models.AuditLog.audit_id == payload.audit_id).first()
        if existing_log:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="AuditId already exists")

    # Create
    obj = models.AuditLog(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)

    # FIX: Use correct AuditLog field: audit_id and User field: full_name (for log consistency)
    crud.audit_log(db, 'AuditLog', obj.audit_id, 'Create', changed_by=current_user.full_name) 
    return obj


# ✅ LIST Audit Logs (Admin only)
@router.get("/", response_model=List[schemas.AuditLogRead], summary="Get list of Audit Log records.")
def list_audit_logs(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Permission Check
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can view audit logs.")

    return db.query(models.AuditLog).offset(offset).limit(limit).all()


# ✅ GET Audit Log by ID (Admin only)
@router.get("/{id}", response_model=schemas.AuditLogRead, summary="Get Audit Log by ID.")
def get_audit_log(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Permission Check
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can view audit logs.")

    # FIX: Use correct AuditLog field name: audit_id
    obj = db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit Log not found")
    return obj


# ✅ UPDATE Audit Log (Admin only)
@router.put("/{id}", response_model=schemas.AuditLogRead, summary="Update Audit Log record.")
def update_audit_log(
    id: str,
    payload: schemas.AuditLogCreate, # Using Create schema for update, assuming all fields are provided
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Permission Check
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can update audit logs.")

    # FIX: Use correct AuditLog field name: audit_id
    obj = db.query(models.AuditLog).filter(models.AuditLog.audit_id == id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit Log not found")

    # Apply updates
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
        
    db.commit()
    db.refresh(obj)

    # FIX: Use correct AuditLog field: audit_id and User field: full_name (for log consistency)
    crud.audit_log(db, 'AuditLog', obj.audit_id, 'Update', changed_by=current_user.full_name)
    return obj