from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from sqlalchemy.orm import Session, joinedload
from jose import jwt, JWTError
from typing import List, Optional
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

def now():
    return datetime.utcnow()

# Auth: Get current user from JWT token in cookie
def get_current_user_from_cookie(
    access_token: str = Cookie(None),
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
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
        raise HTTPException(status_code=401, detail="User not found, please login.")
    return user

# POST - Create Business Unit
@router.post("/", response_model=schemas.BusinessUnitRead, status_code=201, summary="Create a new Business Unit")
def create_business_unit(
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = current_user.role_name

    # Only Admin and BU Head can create
    if role_name not in [models.Role.ADMIN, models.Role.BU_HEAD]:
        raise HTTPException(status_code=403, detail="Only BU Head and Admin can create Business Units")

    # BU_HEADs can only create their own BU
    if role_name == models.Role.BU_HEAD and payload.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="BU Head can only create their own Business Unit")

    # Check for duplicate BUId
    exists = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == payload.BUId).first()
    if exists:
        raise HTTPException(status_code=400, detail="Business Unit with this BUId already exists")

    # Create BU
    new_bu = models.BusinessUnit(**payload.dict())
    db.add(new_bu)
    db.commit()
    db.refresh(new_bu)

    # Audit log
    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=new_bu.BUId,
        action="Create",
        action_performed_by=current_user.userName,
        previous_value="N/A"
    )

    return new_bu

# GET - List Business Units
@router.get("/", response_model=List[schemas.BusinessUnitRead], summary="List Business Units")
def list_business_units(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Roles NOT allowed
    disallowed_roles = [
        models.Role.DEVELOPER,
        models.Role.TEAM_MEMBER,
        models.Role.PROJECT_MANAGER,
        models.Role.DELIVERY_MANAGER,
        models.Role.REVIEWER
    ]

    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission to view Business Units")

    query = db.query(models.BusinessUnit)

    # BU Heads should only see their own BU
    if current_user.role_name == models.Role.BU_HEAD:
        query = query.filter(models.BusinessUnit.BUId == current_user.BUId)

    return query.offset(offset).limit(limit).all()

# GET - Business Unit by ID
@router.get("/{item_id}", response_model=schemas.BusinessUnitRead, summary="Get BU by ID")
def get_business_unit(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == item_id).first()
    if not obj:
        raise HTTPException(status_code=403, detail="BU ID not found")

    if current_user.role_name in [
        models.Role.DEVELOPER,
        models.Role.TEAM_MEMBER,
        models.Role.PROJECT_MANAGER,
        models.Role.DELIVERY_MANAGER,
        models.Role.REVIEWER
    ]:
        raise HTTPException(status_code=403, detail="You do not have permission to view this BU")

    if current_user.role_name == models.Role.BU_HEAD and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="BU Head can only access their own Business Unit")

    return obj

# PUT - Update Business Unit
@router.put("/{item_id}", response_model=schemas.BusinessUnitRead, summary="Update BU")
def update_business_unit(
    item_id: str,
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name != models.Role.BU_HEAD:
        raise HTTPException(status_code=403, detail="Only BU Head can update Business Units")

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    obj.UpdatedAt = now()
    db.commit()
    db.refresh(obj)

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=obj.BUId,
        action="Update",
        action_performed_by=current_user.userName
    )
    return obj

# PATCH - Archive Business Unit
@router.patch("/{item_id}/archive", summary="Archive BU")
def archive_business_unit(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name != models.Role.BU_HEAD:
        raise HTTPException(status_code=403, detail="Only BU Head can archive Business Units")

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    obj.EntityStatus = "Archived"
    obj.UpdatedAt = now()
    db.commit()

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=obj.BUId,
        action="Archive",
        action_performed_by=current_user.userName
    )
    return {"status": "archived"}
