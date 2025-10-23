from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
import logging
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()

SECRET_KEY = "super-secret-key"  # Use environment variables in production!
ALGORITHM = "HS256"

logger = logging.getLogger("uvicorn.error")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user_from_cookie(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> models.User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")

    username = decode_token_and_get_username(access_token)
    user = db.query(models.User).filter(models.User.userName == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def check_permission(current_user: models.User, allowed_roles: List[str]):
    if current_user.role_name not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


@router.post("/", response_model=schemas.RoleMasterRead, summary="Add new RoleMaster record.")
def create_item(
    payload: schemas.RoleMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, ["Admin", "BU Head"])

    # Check duplicate RoleId
    existing_role_id = db.query(models.RoleMaster).filter_by(RoleId=payload.RoleId).first()
    if existing_role_id:
        raise HTTPException(status_code=400, detail="RoleId already exists")

    # Check duplicate RoleName (case-insensitive)
    existing_role_name = db.query(models.RoleMaster).filter(
        models.RoleMaster.RoleName.ilike(payload.RoleName)
    ).first()
    if existing_role_name:
        raise HTTPException(status_code=400, detail="RoleName already exists")

    obj = models.RoleMaster(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'RoleMaster', obj.RoleId, 'Create', changed_by=current_user.userName)
    return obj


@router.get("/", response_model=List[schemas.RoleMasterRead], summary="Get list of RoleMaster records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # All authenticated users can view roles
    query = db.query(models.RoleMaster)
    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.RoleMasterRead, summary="Get RoleMaster by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.RoleMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RoleMaster not found")
    return obj


@router.put("/{item_id}", response_model=schemas.RoleMasterRead, summary="Update RoleMaster record.")
def update_item(
    item_id: str,
    payload: schemas.RoleMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, ["Admin", "BU Head"])

    obj = db.query(models.RoleMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RoleMaster not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'RoleMaster', obj.RoleId, 'Update', changed_by=current_user.userName)
    return obj
