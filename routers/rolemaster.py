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
<<<<<<< HEAD
    check_permission(current_user, ["ADMIN", "BU HEAD"])
=======
    check_permission(current_user, ["Admin", "BU Head"])
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

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

<<<<<<< HEAD
    crud.audit_log(db, 'RoleMaster', obj.RoleId, 'Create',changed_by=current_user.UserId)
=======
    crud.audit_log(db, 'RoleMaster', obj.RoleId, 'Create', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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


<<<<<<< HEAD
@router.get("/{id}", response_model=schemas.RoleMasterRead, summary="Get RoleMaster by ID.")
def get_item(
    id: str,
=======
@router.get("/{item_id}", response_model=schemas.RoleMasterRead, summary="Get RoleMaster by ID.")
def get_item(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.RoleMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RoleMaster not found")
    return obj


<<<<<<< HEAD

@router.patch("/{id}", response_model=schemas.RoleMasterRead, summary="Partially update a Role Master record.")
def update_role_master_partial(
    id: str,
    payload: schemas.RoleMasterUpdate, # Schema with Optional fields for partial update
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    
    # 1. Permission Check
    # RoleMaster is a critical table; modification is typically restricted to only ADMIN.
    if role_name != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only ADMIN is authorized to modify Role records.")

    # 2. Fetch the RoleMaster record
    obj = db.query(models.RoleMaster).filter(
        models.RoleMaster.RoleId == id
        # NOTE: RoleMaster records are usually not 'Archived', but deleted or made inactive.
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    # 3. Perform Update
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    # Assuming the RoleMaster model has an UpdatedAt column
    if hasattr(obj, 'UpdatedAt'):
        obj.UpdatedAt = now() 
        
    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    # NOTE: Assuming crud.audit_log takes the RoleId and the current user's ID.
    crud.audit_log(
        db, 
        'RoleMaster', 
        obj.RoleId, 
        'Update (Partial)', 
        changed_by=current_user.UserId 
    )
    
    return obj


@router.put("/{id}", response_model=schemas.RoleMasterRead, summary="Update RoleMaster record.")
def update_item(
    id: str,
=======
@router.put("/{item_id}", response_model=schemas.RoleMasterRead, summary="Update RoleMaster record.")
def update_item(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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

<<<<<<< HEAD
    crud.audit_log(db, 'RoleMaster', obj.RoleId, 'Update', changed_by=current_user.UserId)
=======
    crud.audit_log(db, 'RoleMaster', obj.RoleId, 'Update', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj
