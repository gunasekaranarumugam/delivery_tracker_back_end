from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime

# Assuming these imports are correct
from main import models, schemas, crud
from main.database import get_db
# Assuming the helper functions are in a utility module or copied here
#from main.utils import get_user_role_and_bu, get_employee_by_user 

router = APIRouter()

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


# --- UTILITY FUNCTIONS (Corrected/Standardized) ---

def decode_token_and_get_username(token: str) -> str:
    try:
        # The token subject is the full_name
        payload = jwt.decode(token.strip(), SECRET_KEY, algorithms=[ALGORITHM])
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
    """Retrieves the User object based on the token."""
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # FIX: Use correct user field: full_name
    full_name = decode_token_and_get_username(token)
    user = db.query(models.User).filter(models.User.full_name == full_name).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

# Assuming get_user_role_and_bu(db, user) is available and returns (role_name, user_bu_id)
# from the previous Project router example.

# ------------------------- CREATE DELIVERABLE -------------------------

@router.post("/", response_model=schemas.DeliverableRead, status_code=status.HTTP_201_CREATED, summary="Add new Deliverable")
def create_deliverable(
    payload: schemas.DeliverableCreate, # Assuming schema has project_id, deliverable_name, etc.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    # 1. Permission Check
    allowed_roles = [models.Role.PROJECT_MANAGER, models.Role.DELIVERY_MANAGER, models.Role.ADMIN]
    if role_name not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create deliverables")

    # 2. Project and BU Checks (Project must exist and user must be in the Project's BU)
    # FIX: Use correct Project field: project_id
    project = db.query(models.Project).filter(
        models.Project.project_id == payload.project_id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # BU restriction: PM/DM must be in the same BU as the Project
    # FIX: Check user's BU against the Project's BU
    if role_name in [models.Role.PROJECT_MANAGER, models.Role.DELIVERY_MANAGER]:
        # FIX: Use project.business_unit_id
        if not user_bu_id or project.business_unit_id != user_bu_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create deliverables for a project outside your Business Unit.")

    # 3. Deliverable ID check
    # FIX: Use correct Deliverable field: deliverable_id
    existing = db.query(models.Deliverable).filter(
        models.Deliverable.deliverable_id == payload.deliverable_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DeliverableId already exists")

    # 4. Create Deliverable
    deliverable = models.Deliverable(
        **payload.model_dump(exclude_unset=True),
        createdby=current_user.user_id, # FIX: Use correct user field: user_id
    )
    # Note: Deliverable model does not have ProjectManagerId, removing that check and assignment.
    # If the schema had project_manager_id, it would be an incorrect field on the Deliverable model.

    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)

    # FIX: Use correct Deliverable and User fields for audit log
    crud.audit_log(db, 'Deliverable', deliverable.deliverable_id, 'Create', changed_by=current_user.user_id) 
    return deliverable


# ------------------------- LIST DELIVERABLES -------------------------

@router.get("/", response_model=List[schemas.DeliverableRead], summary="List deliverables")
def list_deliverables(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    disallowed_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.REVIEWER]
    if role_name in disallowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view deliverables")

    query = db.query(models.Deliverable)

    # BU filter (except for BU Head and Admin)
    if role_name not in [models.Role.BU_HEAD, models.Role.ADMIN]:
        # Filter: Join Deliverable to Project, then filter by Project's BU ID
        # FIX: Join Deliverable to Project on project_id and filter by Project.business_unit_id
        if user_bu_id:
            query = query.join(models.Project).filter(
                models.Project.business_unit_id == user_bu_id
            )
        else:
            # User has an allowed role (e.g., PM, DM) but no BU linked (error should've been raised in helper)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User's BU is not defined for filtering.")


    return query.offset(offset).limit(limit).all()


# ------------------------- GET DELIVERABLE BY ID -------------------------

@router.get("/{id}", response_model=schemas.DeliverableRead, summary="Get deliverable by ID")
def get_deliverable(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    # FIX: Use correct Deliverable field: deliverable_id
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
    if not deliverable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    project = db.query(models.Project).filter(models.Project.project_id == deliverable.project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated Project not found")


    disallowed_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.REVIEWER]
    if role_name in disallowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this deliverable")

    # BU check: PM/DM must be in the same BU as the Project
    if role_name not in [models.Role.BU_HEAD, models.Role.ADMIN]:
        # FIX: Check Project's BU ID
        if project.business_unit_id != user_bu_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this deliverable outside your BU")

    return deliverable


# ------------------------- UPDATE DELIVERABLE -------------------------

@router.put("/{id}", response_model=schemas.DeliverableRead, summary="Update Deliverable")
def update_deliverable(
    id: str,
    payload: schemas.DeliverableCreate, # Typically, an Update schema is used, but using Create as requested
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    if role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER, models.Role.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update deliverables")

    # FIX: Use correct Deliverable field: deliverable_id
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
    if not deliverable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    project = db.query(models.Project).filter(models.Project.project_id == deliverable.project_id).first()
    if not project:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated Project not found")


    # PM/DM restriction: Cannot update deliverables outside their BU
    if role_name == models.Role.PROJECT_MANAGER and project.business_unit_id != user_bu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update deliverables outside your BU")

    # Apply updates
    # FIX: Use payload.model_dump(exclude_unset=True) for standard Pydantic update
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(deliverable, k, v)

    # FIX: Use correct model field: updatedat
    deliverable.updatedat = datetime.utcnow()
    db.commit()
    db.refresh(deliverable)

    # FIX: Use correct Deliverable and User fields for audit log
    crud.audit_log(db, 'Deliverable', deliverable.deliverable_id, 'Update', changed_by=current_user.user_id)
    return deliverable


# ------------------------- ARCHIVE DELIVERABLE -------------------------

@router.patch("/{id}/archive", summary="Archive Deliverable")
def archive_deliverable(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    if role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER, models.Role.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to archive deliverables")

    # FIX: Use correct Deliverable field: deliverable_id
    deliverable = db.query(models.Deliverable).filter(models.Deliverable.deliverable_id == id).first()
    if not deliverable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    project = db.query(models.Project).filter(models.Project.project_id == deliverable.project_id).first()
    if not project:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated Project not found")

    # PM/DM restriction: Cannot archive deliverables outside their BU
    if role_name == models.Role.PROJECT_MANAGER and project.business_unit_id != user_bu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot archive deliverables outside your BU")

    # FIX: Use correct model fields: entitystatus and updatedat
    deliverable.entitystatus = "Archived"
    deliverable.updatedat = datetime.utcnow()
    db.commit()

    # FIX: Use correct Deliverable and User fields for audit log
    crud.audit_log(db, 'Deliverable', deliverable.deliverable_id, 'Archive', changed_by=current_user.user_id)
    return {"status": "archived"}