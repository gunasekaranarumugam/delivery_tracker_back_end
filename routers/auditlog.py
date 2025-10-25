from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
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
    token: Optional[str] = Depends(oauth2_scheme),
) -> models.User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.userName == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ✅ CREATE Audit Log (Admin only)
@router.post("/", response_model=schemas.AuditLogRead, summary="Add new Audit Log record.")
def create_audit_log(
    payload: schemas.AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin can create audit logs.")

<<<<<<< HEAD
    if hasattr(payload, 'AuditLogId'):
        existing_log = db.query(models.AuditLog).filter_by(AuditLogId=payload.AuditLogId).first()
=======
    if hasattr(payload, 'AuditId'):
        existing_log = db.query(models.AuditLog).filter_by(AuditId=payload.AuditId).first()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        if existing_log:
            raise HTTPException(status_code=400, detail="AuditId already exists")

    obj = models.AuditLog(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

<<<<<<< HEAD
    crud.audit_log(db, 'AuditLog', obj.AuditLogId, 'Create', changed_by=current_user.userName)
=======
    crud.audit_log(db, 'AuditLog', obj.AuditId, 'Create', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj


# ✅ LIST Audit Logs (Admin only)
@router.get("/", response_model=List[schemas.AuditLogRead], summary="Get list of Audit Log records.")
def list_audit_logs(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin can view audit logs.")

    return db.query(models.AuditLog).offset(offset).limit(limit).all()


# ✅ GET Audit Log by ID (Admin only)
<<<<<<< HEAD
@router.get("/{id}", response_model=schemas.AuditLogRead, summary="Get Audit Log by ID.")
def get_audit_log(
    id: str,
=======
@router.get("/{item_id}", response_model=schemas.AuditLogRead, summary="Get Audit Log by ID.")
def get_audit_log(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin can view audit logs.")

<<<<<<< HEAD
    obj = db.query(models.AuditLog).get(id)
=======
    obj = db.query(models.AuditLog).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Audit Log not found")
    return obj


# ✅ UPDATE Audit Log (Admin only)
<<<<<<< HEAD
@router.put("/{id}", response_model=schemas.AuditLogRead, summary="Update Audit Log record.")
def update_audit_log(
    id: str,
=======
@router.put("/{item_id}", response_model=schemas.AuditLogRead, summary="Update Audit Log record.")
def update_audit_log(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    payload: schemas.AuditLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin can update audit logs.")

<<<<<<< HEAD
    obj = db.query(models.AuditLog).get(id)
=======
    obj = db.query(models.AuditLog).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Audit Log not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

<<<<<<< HEAD
    crud.audit_log(db, 'AuditLog', obj.AuditLogId, 'Update', changed_by=current_user.userName)
=======
    crud.audit_log(db, 'AuditLog', obj.AuditId, 'Update', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj
