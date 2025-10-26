from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List, Optional
from datetime import datetime

# Assuming these are correctly imported and include your defined models
from main import models, schemas, crud 
from main.database import get_db

router = APIRouter()
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

# Note: OAuth2PasswordBearer is usually imported from the auth file, but kept here for context
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

def now():
    return datetime.utcnow()

def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # The token subject is the full_name, not a separate username field
        full_name = payload.get("sub") 
        if not full_name:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return full_name
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_from_cookie(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Retrieves the User object based on the token in the Authorization header or cookie."""
    # Fallback to cookie token if Authorization header missing
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # FIX 1: Use full_name (token subject) and models.User.full_name (DB column)
    full_name = decode_token_and_get_username(token) 
    user = db.query(models.User).filter(models.User.full_name == full_name).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ----------------------------------------------------------------------
# ⚡ Dependency: Retrieves role name and EmployeeId using model relationships
# ----------------------------------------------------------------------
# NOTE: This dependency relies on the User model having relationships defined 
# to access role_name and employee/EmployeeId. Assuming these relationships 
# (e.g., User.employee -> Employee, User.role_name property) exist in your models file.

def get_auth_employee_info(current_user: models.User = Depends(get_current_user_from_cookie)):
    """
    Retrieves the role name, EmployeeId, and User object using model relationships.
    """
    # Assuming role_name and employee are properties/relationships on models.User
    role_name = current_user.role_name
    employee = current_user.employee
    
    if not employee:
        raise HTTPException(status_code=403, detail="Authorization context missing: User is not linked to an active Employee record.")

    # Assuming the Employee model uses 'employee_id' or 'EmployeeId' as its primary key
    # Based on Project model, the FK is 'employee.employee_id' but BusinessUnit uses 'employee.EmployeeId'. 
    # Sticking to the BU model's reference: 'EmployeeId'
    user_employee_id = employee.EmployeeId
    
    return role_name, user_employee_id, current_user # Return user as well for audit logging

# ----------------------------------------------------------------------
## Business Unit Endpoints

# ✅ POST - Create Business Unit
@router.post("/", response_model=schemas.BusinessUnitRead, status_code=status.HTTP_201_CREATED, summary="Create a new Business Unit")
def create_business_unit(
    payload: schemas.BusinessUnitCreate, # Assuming this schema has fields like business_unit_name, business_unit_head_id, etc.
    db: Session = Depends(get_db),
    auth_data: tuple = Depends(get_auth_employee_info),
):
    role_name, user_employee_id, current_user = auth_data
    
    # Check Authorization (Assuming models.Role is an enum or class with constants)
    if role_name not in [models.Role.ADMIN, models.Role.BU_HEAD]:
        raise HTTPException(status_code=403, detail="Only BU HEAD and ADMIN can create Business Units")

    # If the BU HEAD is creating, they must be the one specified as BUHead
    # FIX 2: Use payload.business_unit_head_id to match model
    if role_name == models.Role.BU_HEAD and payload.business_unit_head_id != user_employee_id:
        raise HTTPException(status_code=403, detail="BU HEAD can only create their own Business Unit")

    # FIX 3: Use the correct column name: models.BusinessUnit.business_unit_name (checking by name is safer than an ID that might not be auto-generated yet)
    exists = db.query(models.BusinessUnit).filter(
        models.BusinessUnit.business_unit_name == payload.business_unit_name
    ).first()
    
    if exists:
        raise HTTPException(status_code=400, detail="Business Unit with this name already exists")

    # FIX 4: Add createdby and set initial createdat/updatedat (though models do this by default)
    # Note: Assuming payload.dict() correctly maps to model fields
    bu_data = payload.dict()
    bu_data["createdby"] = current_user.user_id # FIX 5: Use current_user.user_id
    # Note: business_unit_id should be generated by a utility, assumed to be handled by CRUD or a pre-save hook.

    new_bu = models.BusinessUnit(**bu_data)
    
    db.add(new_bu)
    db.commit()
    db.refresh(new_bu)

    # FIX 6: Use new_bu.business_unit_id and current_user.user_id for audit log
    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=new_bu.business_unit_id,
        action="Create",
        action_performed_by=current_user.user_id,
        previous_value="N/A"
    )

    return new_bu

# ----------------------------------------------------------------------

# ✅ GET - List Business Units
@router.get("/", response_model=List[schemas.BusinessUnitRead], summary="List Business Units")
def list_business_units(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    auth_data: tuple = Depends(get_auth_employee_info),
):
    role_name, user_employee_id, _ = auth_data

    disallowed_roles = [
        models.Role.DEVELOPER, 
        models.Role.TEAM_MEMBER, 
        models.Role.PROJECT_MANAGER, 
        models.Role.DELIVERY_MANAGER, 
        models.Role.REVIEWER
    ]

    if role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission to view Business Units")

    query = db.query(models.BusinessUnit)

    # If BU HEAD, filter to only show BU's they head
    # FIX 7: Use models.BusinessUnit.business_unit_head_id
    if role_name == models.Role.BU_HEAD and user_employee_id:
        query = query.filter(models.BusinessUnit.business_unit_head_id == user_employee_id)

    return query.offset(offset).limit(limit).all()

# ----------------------------------------------------------------------

# ✅ GET - Business Unit by ID
@router.get("/{id}", response_model=schemas.BusinessUnitRead, summary="Get BU by ID")
def get_business_unit(
    id: str,
    db: Session = Depends(get_db),
    auth_data: tuple = Depends(get_auth_employee_info),
):
    role_name, user_employee_id, _ = auth_data

    # FIX 8: Use models.BusinessUnit.business_unit_id
    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.business_unit_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="BU not found")

    disallowed_roles = [
        models.Role.DEVELOPER, 
        models.Role.TEAM_MEMBER, 
        models.Role.PROJECT_MANAGER, 
        models.Role.DELIVERY_MANAGER, 
        models.Role.REVIEWER
    ]

    if role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="You do not have permission to view this BU")

    # If BU HEAD, check if they are the head of this specific BU
    # FIX 9: Use obj.business_unit_head_id
    if role_name == models.Role.BU_HEAD and obj.business_unit_head_id != user_employee_id:
        raise HTTPException(status_code=403, detail="BU HEAD can only access their own Business Unit")

    return obj

# ----------------------------------------------------------------------

# ✅ PUT - Update Business Unit
@router.put("/{id}", response_model=schemas.BusinessUnitRead, summary="Update BU")
def update_business_unit(
    id: str,
    payload: schemas.BusinessUnitCreate,
    db: Session = Depends(get_db),
    auth_data: tuple = Depends(get_auth_employee_info),
):
    role_name, user_employee_id, current_user = auth_data

    # Restriction: Only BU HEAD can update Business Units (assuming ADMIN is excluded for tight control)
    if role_name != models.Role.BU_HEAD:
        raise HTTPException(status_code=403, detail="Only BU HEAD can update Business Units")

    # FIX 10: Use models.BusinessUnit.business_unit_id
    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.business_unit_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    # Restriction: BU HEAD can only update their own BU
    # FIX 11: Use obj.business_unit_head_id
    if obj.business_unit_head_id != user_employee_id:
        raise HTTPException(status_code=403, detail="You can only update your own Business Unit")
    
    # Apply updates from payload
    for key, value in payload.dict(exclude_unset=True).items():
        # NOTE: This assumes the schema fields match the model fields exactly.
        setattr(obj, key, value)
        
    # FIX 12: Use obj.updatedat and obj.createdby (though createdby is set on creation)
    obj.updatedat = now()
    # It's good practice to update the 'createdby' FK to reflect who performed the update if needed,
    # but based on your models, we'll stick to 'updatedat' for the timestamp.
    
    db.commit()
    db.refresh(obj)

    # FIX 13: Use obj.business_unit_id and current_user.user_id for audit log
    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=obj.business_unit_id,
        action="Update",
        action_performed_by=current_user.user_id
    )
    return obj

# ----------------------------------------------------------------------

# ✅ PATCH - Archive Business Unit
@router.patch("/{id}/archive", summary="Archive BU")
def archive_business_unit(
    id: str,
    db: Session = Depends(get_db),
    auth_data: tuple = Depends(get_auth_employee_info),
):
    role_name, user_employee_id, current_user = auth_data

    if role_name != models.Role.BU_HEAD:
        raise HTTPException(status_code=403, detail="Only BU HEAD can archive Business Units")

    # FIX 14: Use models.BusinessUnit.business_unit_id
    obj = db.query(models.BusinessUnit).filter(models.BusinessUnit.business_unit_id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Business Unit not found")

    # Restriction: BU HEAD can only archive their own BU
    # FIX 15: Use obj.business_unit_head_id
    if obj.business_unit_head_id != user_employee_id:
        raise HTTPException(status_code=403, detail="You can only archive your own Business Unit")

    # FIX 16: Use obj.entitystatus and obj.updatedat
    obj.entitystatus = "ARCHIVED"
    obj.updatedat = now()
    db.commit()

    # FIX 17: Use obj.business_unit_id and current_user.user_id for audit log
    crud.audit_log(
        db,
        entity_type="BusinessUnit",
        entity_id=obj.business_unit_id,
        action="Archive",
        action_performed_by=current_user.user_id
    )
    return {"status": "archived"}