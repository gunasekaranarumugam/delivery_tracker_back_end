from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List, Optional
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def now():
    return datetime.utcnow()


def get_current_user_from_cookie(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),  # reads Authorization header bearer token if present
    db: Session = Depends(get_db),
) -> models.User:
    # Fallback to cookie token if Authorization header missing
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    username = decode_token_and_get_username(token)
    user = db.query(models.User).filter(models.User.userName == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# 🔹 Helper: Get the employee and role for a given user (match by email)
def get_user_role_and_bu(db: Session, user: models.User):
    employee = db.query(models.Employee).filter(models.Employee.Email == user.emailID).first()
    role_name = None
    bu_id = None

    if employee:
        if employee.RoleId:
            role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleId == employee.RoleId).first()
            role_name = role.RoleName if role else None
        if employee.BUId:
            bu_id = employee.BUId

    return role_name, bu_id


# ✅ POST - Create Business Unit
@router.post("/", response_model=schemas.BusinessUnitRead, status_code=201, summary="Create a new Business Unit")
def create_business_unit(
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    if role_name not in ["ADMIN", "BU HEAD"]:
        raise HTTPException(status_code=403, detail="Only BU HEAD and ADMIN can create Business Units")

    if role_name == "BU HEAD" and payload.BUHeadEmail != current_user.emailID:
        raise HTTPException(status_code=403, detail="BU HEAD can only create their own Business Unit")

    exists = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == payload.BUId).first()
    if exists:
        raise HTTPException(status_code=400, detail="Business Unit with this BUId already exists")

    new_bu = models.BusinessUnit(**payload.dict())
    db.add(new_bu)
    db.commit()
    db.refresh(new_bu)

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=new_bu.BUId,
        action="Create",
        action_performed_by=current_user.UserId,
        previous_value="N/A"
    )

    return new_bu


# ✅ GET - List Business Units
@router.get("/", response_model=List[schemas.BusinessUnitRead], summary="List Business Units")
def list_business_units(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    disallowed_roles = ["DEVELOPER", "TEAM MEMBER", "PROJECT MANAGER", "DELIVERY MANAGER", "REVIEWER"]

    if role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission to view Business Units")

    query = db.query(models.BusinessUnit)

    if role_name == "BU HEAD":
        query = query.filter(models.BusinessUnit.BUHeadEmail == current_user.emailID)

    return query.offset(offset).limit(limit).all()


# ✅ GET - Business Unit by ID
@router.get("/{id}", response_model=schemas.BusinessUnitRead, summary="Get BU by ID")
def get_business_unit(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="BU not found")

    disallowed_roles = ["DEVELOPER", "TEAM MEMBER", "PROJECT MANAGER", "DELIVERY MANAGER", "REVIEWER"]

    if role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission to view this BU")

    if role_name == "BU HEAD" and obj.BUHeadEmail != current_user.emailID:
        raise HTTPException(status_code=403, detail="BU HEAD can only access their own Business Unit")

    return obj


# ✅ PUT - Update Business Unit
@router.put("/{id}", response_model=schemas.BusinessUnitRead, summary="Update BU")
def update_business_unit(
    id: str,
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    if role_name != "BU HEAD":
        raise HTTPException(status_code=403, detail="Only BU HEAD can update Business Units")

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    if obj.BUHeadEmail != current_user.emailID:
        raise HTTPException(status_code=403, detail="You can only update your own Business Unit")

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
        action_performed_by=current_user.UserId
    )
    return obj


# ✅ PATCH - Archive Business Unit
@router.patch("/{id}/archive", summary="Archive BU")
def archive_business_unit(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    if role_name != "BU HEAD":
        raise HTTPException(status_code=403, detail="Only BU HEAD can archive Business Units")

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    if obj.BUHeadEmail != current_user.emailID:
        raise HTTPException(status_code=403, detail="You can only archive your own Business Unit")

    obj.EntityStatus = "ARCHIVED"
    obj.UpdatedAt = now()
    db.commit()

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=obj.BUId,
        action="Archive",
        action_performed_by=current_user.UserId
    )
    return {"status": "archived"}
