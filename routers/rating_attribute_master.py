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
    user = db.query(models.User).filter(models.User.UserName == username).first()
    if not user:
        logger.debug(f"User not found for username: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def check_permission(current_user: models.User, allowed_roles: List[str]):
    # NOTE: Assuming models.User has a 'role_name' attribute (which is common) 
    # and that models.Role is a class/enum containing the strings 'ADMIN' and 'BU_HEAD'.
    if current_user.role_name not in allowed_roles:
        logger.warning(f"User '{current_user.userName}' with role '{current_user.role_name}' denied access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


# ----------------------------------------------------------------------
#                             RATING ATTRIBUTE ENDPOINTS
# ----------------------------------------------------------------------

@router.post("/", response_model=schemas.RatingAttributeMasterRead, status_code=status.HTTP_201_CREATED)
def create_attribute(
    attribute_in: schemas.RatingAttributeMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, ["ADMIN", "BU_HEAD"]) # Using strings based on common practice, adjust if models.Role is an object

    existing_attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeName == attribute_in.AttributeName
    ).first()

    if existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attribute with name '{attribute_in.AttributeName}' already exists."
        )

    attribute_id = str(uuid.uuid4())
    
    # NOTE: Assuming 'Weight' has been added to RatingAttributeMasterCreate schema
    # NOTE: Assuming 'CreatedById' and 'EntityStatus' exist on models.RatingAttributeMaster
    
    db_attribute = models.RatingAttributeMaster(
        AttributeId=attribute_id,
        AttributeName=attribute_in.AttributeName,
        Description=attribute_in.Description,
        # The 'Weight' field must be added to RatingAttributeMasterCreate schema for this to work
        # If Weight is optional in the schema, you can use: Weight=attribute_in.Weight or 1.0,
        # Based on the original code, I'm assuming Weight is a field on the schema:
        Weight=getattr(attribute_in, 'Weight', 1.0), 
        CreatedById=current_user.UserId,
        CreatedAt=datetime.utcnow(),
        EntityStatus="Active"
    )
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)

    crud.audit_log(db, "RatingAttributeMaster", db_attribute.AttributeId, "Create", changed_by=current_user.UserId)

    return db_attribute


@router.get("/", response_model=List[schemas.RatingAttributeMasterRead]) # Corrected response model
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


@router.get("/{id}", response_model=schemas.RatingAttributeMasterRead) # Corrected response model
def get_attribute(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == id,
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    return attribute


@router.put("/{id}", response_model=schemas.RatingAttributeMasterRead) # Corrected response model
def update_attribute(
    id: str,
    attribute_in: schemas.RatingAttributeMasterUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, ["ADMIN", "BU_HEAD"]) # Using strings

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == id,
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    # This loop correctly updates fields passed in the request body
    update_data = attribute_in.dict(exclude_unset=True)
    
    # Update ORM object fields
    for field, value in update_data.items():
        setattr(attribute, field, value)

    # Set auditing fields
    attribute.UpdatedAt = datetime.utcnow()
    # NOTE: Assuming 'UpdatedById' exists on models.RatingAttributeMaster
    setattr(attribute, 'UpdatedById', current_user.UserId) 

    db.commit()
    db.refresh(attribute)

    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Update", changed_by=current_user.UserId)

    return attribute


@router.patch("/{id}/archive", status_code=status.HTTP_200_OK)
def archive_attribute(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, ["ADMIN", "BU_HEAD"]) # Using strings

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == id,
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()

    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    attribute.EntityStatus = "Archived"
    attribute.UpdatedAt = datetime.utcnow()
    # NOTE: Assuming 'UpdatedById' exists on models.RatingAttributeMaster
    setattr(attribute, 'UpdatedById', current_user.UserId) 

    db.commit()

    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Archive", changed_by=current_user.UserId)

    return {"status": "archived", "attribute_id": attribute.AttributeId}