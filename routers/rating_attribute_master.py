from fastapi import APIRouter, HTTPException, Depends, status, Cookie
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from jose import jwt, JWTError
from main import models, schemas, crud
from main.database import get_db
from datetime import datetime
import logging
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()

# Use environment variables or config in production
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

logger = logging.getLogger("uvicorn.error")


def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            logger.debug("Token payload missing 'sub'")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user_from_cookie(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),  
) -> models.User:
    if not access_token:
        logger.debug("Access token cookie is missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")

    username = decode_token_and_get_username(access_token)
    user = db.query(models.User).filter(models.User.userName == username).first()
    if not user:
        logger.debug(f"User not found for username: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def check_permission(current_user: models.User, allowed_roles: List[str]):
    if current_user.role_name not in allowed_roles:
        logger.warning(f"User '{current_user.userName}' with role '{current_user.role_name}' denied access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


@router.post("/", response_model=schemas.RatingAttributeMaster, status_code=status.HTTP_201_CREATED)
def create_attribute(
    attribute_in: schemas.RatingAttributeMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD])

    existing_attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeName == attribute_in.AttributeName
    ).first()

    if existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attribute with name '{attribute_in.AttributeName}' already exists."
        )

    attribute_id = str(uuid.uuid4())
    db_attribute = models.RatingAttributeMaster(
        AttributeId=attribute_id,
        AttributeName=attribute_in.AttributeName,
        Description=attribute_in.Description,
        Weight=attribute_in.Weight or 1.0,
        CreatedById=current_user.UserId,
        CreatedAt=datetime.utcnow(),
        EntityStatus="Active"
    )
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)

    crud.audit_log(db, "RatingAttributeMaster", db_attribute.AttributeId, "Create", changed_by=current_user.userName)

    return db_attribute


@router.get("/", response_model=List[schemas.RatingAttributeMaster])
def list_attributes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # All authenticated users can read
    return db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).offset(skip).limit(limit).all()


@router.get("/{attribute_id}", response_model=schemas.RatingAttributeMaster)
def get_attribute(
    attribute_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == attribute_id,
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    return attribute


@router.put("/{attribute_id}", response_model=schemas.RatingAttributeMaster)
def update_attribute(
    attribute_id: str,
    attribute_in: schemas.RatingAttributeMasterUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD])

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == attribute_id,
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    for field, value in attribute_in.dict(exclude_unset=True).items():
        setattr(attribute, field, value)

    attribute.UpdatedAt = datetime.utcnow()
    attribute.UpdatedById = current_user.UserId

    db.commit()
    db.refresh(attribute)

    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Update", changed_by=current_user.userName)

    return attribute


@router.patch("/{attribute_id}/archive", status_code=status.HTTP_200_OK)
def archive_attribute(
    attribute_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD])

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == attribute_id,
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()

    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    attribute.EntityStatus = "Archived"
    attribute.UpdatedAt = datetime.utcnow()
    attribute.UpdatedById = current_user.UserId

    db.commit()

    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Archive", changed_by=current_user.userName)

    return {"status": "archived", "attribute_id": attribute.AttributeId}
