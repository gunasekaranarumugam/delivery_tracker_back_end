<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, Request
from sqlalchemy.orm import Session
=======
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from sqlalchemy.orm import Session, joinedload
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
from jose import jwt, JWTError
from typing import List, Optional
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

<<<<<<< HEAD
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
=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
@router.post("/", response_model=schemas.BusinessUnitRead, status_code=201, summary="Create a new Business Unit")
def create_business_unit(
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
<<<<<<< HEAD
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    if role_name not in ["ADMIN", "BU HEAD"]:
        raise HTTPException(status_code=403, detail="Only BU HEAD and ADMIN can create Business Units")

    if role_name == "BU HEAD" and payload.BUHeadEmail != current_user.emailID:
        raise HTTPException(status_code=403, detail="BU HEAD can only create their own Business Unit")

=======
    role_name = current_user.role_name

    # Only Admin and BU Head can create
    if role_name not in [models.Role.ADMIN, models.Role.BU_HEAD]:
        raise HTTPException(status_code=403, detail="Only BU Head and Admin can create Business Units")

    # BU_HEADs can only create their own BU
    if role_name == models.Role.BU_HEAD and payload.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="BU Head can only create their own Business Unit")

    # Check for duplicate BUId
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    exists = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == payload.BUId).first()
    if exists:
        raise HTTPException(status_code=400, detail="Business Unit with this BUId already exists")

<<<<<<< HEAD
=======
    # Create BU
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    new_bu = models.BusinessUnit(**payload.dict())
    db.add(new_bu)
    db.commit()
    db.refresh(new_bu)

<<<<<<< HEAD
=======
    # Audit log
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=new_bu.BUId,
        action="Create",
<<<<<<< HEAD
        action_performed_by=current_user.UserId,
=======
        action_performed_by=current_user.userName,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        previous_value="N/A"
    )

    return new_bu

<<<<<<< HEAD

# ✅ GET - List Business Units
=======
# GET - List Business Units
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
@router.get("/", response_model=List[schemas.BusinessUnitRead], summary="List Business Units")
def list_business_units(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
<<<<<<< HEAD
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    disallowed_roles = ["DEVELOPER", "TEAM MEMBER", "PROJECT MANAGER", "DELIVERY MANAGER", "REVIEWER"]

    if role_name in disallowed_roles:
=======
    # Roles NOT allowed
    disallowed_roles = [
        models.Role.DEVELOPER,
        models.Role.TEAM_MEMBER,
        models.Role.PROJECT_MANAGER,
        models.Role.DELIVERY_MANAGER,
        models.Role.REVIEWER
    ]

    if current_user.role_name in disallowed_roles:
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
        raise HTTPException(status_code=403, detail="You do not have permission to view Business Units")

    query = db.query(models.BusinessUnit)

<<<<<<< HEAD
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
=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
<<<<<<< HEAD
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    if role_name != "BU HEAD":
        raise HTTPException(status_code=403, detail="Only BU HEAD can update Business Units")

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    if obj.BUHeadEmail != current_user.emailID:
        raise HTTPException(status_code=403, detail="You can only update your own Business Unit")

=======
    if current_user.role_name != models.Role.BU_HEAD:
        raise HTTPException(status_code=403, detail="Only BU Head can update Business Units")

    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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
<<<<<<< HEAD
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
=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    obj.UpdatedAt = now()
    db.commit()

    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=obj.BUId,
        action="Archive",
<<<<<<< HEAD
        action_performed_by=current_user.UserId
=======
        action_performed_by=current_user.userName
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    )
    return {"status": "archived"}
