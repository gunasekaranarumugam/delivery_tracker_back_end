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
<<<<<<< HEAD
    token: Optional[str] = Depends(oauth2_scheme),
=======
    token: Optional[str] = Depends(oauth2_scheme),  
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
) -> models.User:
    if not access_token:
        logger.debug("Access token cookie is missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")

    username = decode_token_and_get_username(access_token)
<<<<<<< HEAD
    user = db.query(models.User).filter(models.User.UserName == username).first()
=======
    user = db.query(models.User).filter(models.User.userName == username).first()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not user:
        logger.debug(f"User not found for username: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def check_permission(current_user: models.User, allowed_roles: List[str]):
<<<<<<< HEAD
    # NOTE: Assuming models.User has a 'role_name' attribute (which is common) 
    # and that models.Role is a class/enum containing the strings 'ADMIN' and 'BU_HEAD'.
=======
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if current_user.role_name not in allowed_roles:
        logger.warning(f"User '{current_user.userName}' with role '{current_user.role_name}' denied access")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


<<<<<<< HEAD
# ----------------------------------------------------------------------
#                             RATING ATTRIBUTE ENDPOINTS
# ----------------------------------------------------------------------

@router.post("/", response_model=schemas.RatingAttributeMasterRead, status_code=status.HTTP_201_CREATED)
=======
@router.post("/", response_model=schemas.RatingAttributeMaster, status_code=status.HTTP_201_CREATED)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
def create_attribute(
    attribute_in: schemas.RatingAttributeMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
<<<<<<< HEAD
    check_permission(current_user, ["ADMIN", "BU_HEAD"]) # Using strings based on common practice, adjust if models.Role is an object
=======
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD])
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

    existing_attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeName == attribute_in.AttributeName
    ).first()

    if existing_attribute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attribute with name '{attribute_in.AttributeName}' already exists."
        )

    attribute_id = str(uuid.uuid4())
<<<<<<< HEAD
    
    # NOTE: Assuming 'Weight' has been added to RatingAttributeMasterCreate schema
    # NOTE: Assuming 'CreatedById' and 'EntityStatus' exist on models.RatingAttributeMaster
    
=======
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    db_attribute = models.RatingAttributeMaster(
        AttributeId=attribute_id,
        AttributeName=attribute_in.AttributeName,
        Description=attribute_in.Description,
<<<<<<< HEAD
        # The 'Weight' field must be added to RatingAttributeMasterCreate schema for this to work
        # If Weight is optional in the schema, you can use: Weight=attribute_in.Weight or 1.0,
        # Based on the original code, I'm assuming Weight is a field on the schema:
        Weight=getattr(attribute_in, 'Weight', 1.0), 
=======
        Weight=attribute_in.Weight or 1.0,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        CreatedById=current_user.UserId,
        CreatedAt=datetime.utcnow(),
        EntityStatus="Active"
    )
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)

<<<<<<< HEAD
    crud.audit_log(db, "RatingAttributeMaster", db_attribute.AttributeId, "Create", changed_by=current_user.UserId)
=======
    crud.audit_log(db, "RatingAttributeMaster", db_attribute.AttributeId, "Create", changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

    return db_attribute


<<<<<<< HEAD
@router.get("/", response_model=List[schemas.RatingAttributeMasterRead]) # Corrected response model
=======
@router.get("/", response_model=List[schemas.RatingAttributeMaster])
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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


<<<<<<< HEAD
@router.get("/{id}", response_model=schemas.RatingAttributeMasterRead) # Corrected response model
def get_attribute(
    id: str,
=======
@router.get("/{attribute_id}", response_model=schemas.RatingAttributeMaster)
def get_attribute(
    attribute_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    attribute = db.query(models.RatingAttributeMaster).filter(
<<<<<<< HEAD
        models.RatingAttributeMaster.AttributeId == id,
=======
        models.RatingAttributeMaster.AttributeId == attribute_id,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    return attribute


<<<<<<< HEAD
@router.put("/{id}", response_model=schemas.RatingAttributeMasterRead) # Corrected response model
def update_attribute(
    id: str,
=======
@router.put("/{attribute_id}", response_model=schemas.RatingAttributeMaster)
def update_attribute(
    attribute_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    attribute_in: schemas.RatingAttributeMasterUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
<<<<<<< HEAD
    check_permission(current_user, ["ADMIN", "BU_HEAD"]) # Using strings

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == id,
=======
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD])

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == attribute_id,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

<<<<<<< HEAD
    # This loop correctly updates fields passed in the request body
    update_data = attribute_in.dict(exclude_unset=True)
    
    # Update ORM object fields
    for field, value in update_data.items():
        setattr(attribute, field, value)

    # Set auditing fields
    attribute.UpdatedAt = datetime.utcnow()
    # NOTE: Assuming 'UpdatedById' exists on models.RatingAttributeMaster
    setattr(attribute, 'UpdatedById', current_user.UserId) 
=======
    for field, value in attribute_in.dict(exclude_unset=True).items():
        setattr(attribute, field, value)

    attribute.UpdatedAt = datetime.utcnow()
    attribute.UpdatedById = current_user.UserId
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

    db.commit()
    db.refresh(attribute)

<<<<<<< HEAD
    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Update", changed_by=current_user.UserId)
=======
    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Update", changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

    return attribute


<<<<<<< HEAD
@router.patch("/{id}/archive", status_code=status.HTTP_200_OK)
def archive_attribute(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, ["ADMIN", "BU_HEAD"]) # Using strings

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == id,
=======
@router.patch("/{attribute_id}/archive", status_code=status.HTTP_200_OK)
def archive_attribute(
    attribute_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD])

    attribute = db.query(models.RatingAttributeMaster).filter(
        models.RatingAttributeMaster.AttributeId == attribute_id,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        models.RatingAttributeMaster.EntityStatus != "Archived"
    ).first()

    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")

    attribute.EntityStatus = "Archived"
    attribute.UpdatedAt = datetime.utcnow()
<<<<<<< HEAD
    # NOTE: Assuming 'UpdatedById' exists on models.RatingAttributeMaster
    setattr(attribute, 'UpdatedById', current_user.UserId) 

    db.commit()

    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Archive", changed_by=current_user.UserId)

    return {"status": "archived", "attribute_id": attribute.AttributeId}
=======
    attribute.UpdatedById = current_user.UserId

    db.commit()

    crud.audit_log(db, "RatingAttributeMaster", attribute.AttributeId, "Archive", changed_by=current_user.userName)

    return {"status": "archived", "attribute_id": attribute.AttributeId}
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
