from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

SECRET_KEY = "super-secret-key"  # Use environment variable in production
ALGORITHM = "HS256"


def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except JWTError:
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )


@router.post("/", response_model=schemas.SkillMasterRead, summary="Add new Skill record.")
def create_item(
    payload: schemas.SkillMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = ["ADMIN", "PROJECT MANAGER"]
    check_permission(current_user, allowed_roles)

    # Check if SkillId already exists
    existing_skill_id = db.query(models.SkillMaster).filter_by(SkillId=payload.SkillId).first()
    if existing_skill_id:
        raise HTTPException(status_code=400, detail="SkillId already exists")

    # Check if SkillName already exists (case-insensitive)
    existing_skill_name = db.query(models.SkillMaster).filter(
        models.SkillMaster.SkillName.ilike(payload.SkillName)
    ).first()
    if existing_skill_name:
        raise HTTPException(status_code=400, detail="SkillName already exists")

    obj = models.SkillMaster(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'SkillMaster', obj.SkillId, 'Create', changed_by=current_user.userName)
    return obj


@router.get("/", response_model=List[schemas.SkillMasterRead], summary="Get list of Skill records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Roles not allowed to view
    disallowed_roles = ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

    query = db.query(models.SkillMaster)
    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.SkillMasterRead, summary="Get Skill by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    disallowed_roles = ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

    obj = db.query(models.SkillMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Skill not found")
    return obj


@router.put("/{item_id}", response_model=schemas.SkillMasterRead, summary="Update Skill record.")
def update_item(
    item_id: str,
    payload: schemas.SkillMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = ["ADMIN", "PROJECT MANAGER"]
    check_permission(current_user, allowed_roles)

    obj = db.query(models.SkillMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Skill not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'SkillMaster', obj.SkillId, 'Update', changed_by=current_user.userName)
    return obj
