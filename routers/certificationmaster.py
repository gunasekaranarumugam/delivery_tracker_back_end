from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from jose import jwt, JWTError
from main import models, schemas, crud
from main.database import get_db
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

# Utility to get current user from token in cookie
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


# ✅ CREATE Certification (Admin only)
@router.post("/", response_model=schemas.CertificationMasterRead, summary="Add new Certification record.")
def create_certification(
    payload: schemas.CertificationMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin can create certifications.")

    existing_cert_id = db.query(models.CertificationMaster).filter_by(CertificationId=payload.CertificationId).first()
    if existing_cert_id:
        raise HTTPException(status_code=400, detail="CertificationId already exists")

    existing_cert_name = db.query(models.CertificationMaster).filter(
        models.CertificationMaster.CertificationName.ilike(payload.CertificationName)
    ).first()
    if existing_cert_name:
        raise HTTPException(status_code=400, detail="CertificationName already exists")

    obj = models.CertificationMaster(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'CertificationMaster', obj.CertificationId, 'Create', changed_by=current_user.userName)
    return obj


# ✅ GET All Certifications (anyone logged in)
@router.get("/", response_model=List[schemas.CertificationMasterRead], summary="Get list of Certification records.")
def list_certifications(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    return db.query(models.CertificationMaster).offset(offset).limit(limit).all()


# ✅ GET Certification by ID (anyone logged in)
@router.get("/{item_id}", response_model=schemas.CertificationMasterRead, summary="Get Certification by ID.")
def get_certification(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.CertificationMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Certification not found")
    return obj


# ✅ UPDATE Certification (Admin only)
@router.put("/{item_id}", response_model=schemas.CertificationMasterRead, summary="Update Certification record.")
def update_certification(
    item_id: str,
    payload: schemas.CertificationMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name != models.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admin can update certifications.")

    obj = db.query(models.CertificationMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Certification not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'CertificationMaster', obj.CertificationId, 'Update', changed_by=current_user.userName)
    return obj
