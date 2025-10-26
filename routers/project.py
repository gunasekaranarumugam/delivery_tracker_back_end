from fastapi import APIRouter, Depends, HTTPException, Cookie, Request, status
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

# Assuming these imports are correct based on your project structure
from main import models, schemas, crud
from main.database import get_db
from main.models import Role # constants class

router = APIRouter()

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

# --- UTILITY FUNCTIONS (Corrected) ---

def decode_token_and_get_username(token: str) -> str:
    try:
        # The token subject is the full_name, not a separate username field
        payload = jwt.decode(token.strip(), SECRET_KEY, algorithms=[ALGORITHM])
        full_name = payload.get("sub")
        if not full_name:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return full_name
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_employee_by_user(db: Session, user: models.User) -> models.Employee:
    """Helper to get the associated Employee object for the current User."""
    employee = db.query(models.Employee).filter(
        # FIX: Use correct user field: email_address
        models.Employee.Email == user.email_address 
    ).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No employee record linked to your user account.")
    return employee


def get_user_role_and_bu(db: Session, user: models.User) -> tuple[str, Optional[str]]:
    """Helper to get the current user's active role name and BU ID."""
    employee = get_employee_by_user(db, user)

    # 1. Get the current employee's active role assignment
    employee_role_link = db.query(models.EmployeeRole).filter(
        models.EmployeeRole.EmployeeId == employee.EmployeeId,
        models.EmployeeRole.EntityStatus == "Active",
        models.EmployeeRole.Active == 1
    ).join(models.RoleMaster).first()

    if not employee_role_link:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no active role assigned.")

    # 2. Get the RoleMaster object
    role = db.query(models.RoleMaster).filter(
        models.RoleMaster.RoleId == employee_role_link.RoleId
    ).first()
    
    # Return RoleName and BUId (assuming models.Employee has a BUId field)
    return role.RoleName if role else "UNKNOWN", employee.BUId

# Corrected Dependency function
def get_current_user_from_cookie(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # FIX: Use full_name (token subject) and models.User.full_name (DB column)
    full_name = decode_token_and_get_username(token)
    user = db.query(models.User).filter(models.User.full_name == full_name).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return user


# ------------------------- CREATE PROJECT -------------------------

@router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED, summary="Create a new project")
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    # 1. Permission Check
    allowed_roles = [Role.BU_HEAD, Role.ADMIN]
    if role_name not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied. Only ADMIN and BU HEAD can create projects.")

    # 2. BU Restriction for BU HEAD
    # FIX: Use correct project field name: business_unit_id
    if role_name == Role.BU_HEAD and payload.business_unit_id != user_bu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="BU HEAD can only create projects within their own BU.")

    # 3. Validate Delivery Manager existence
    # FIX: Use correct payload field name: delivery_manager_id
    dm_employee = db.query(models.Employee).filter(
        models.Employee.EmployeeId == payload.delivery_manager_id.strip().upper()
    ).first()

    if not dm_employee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delivery Manager EmployeeId not found.")

    # 4. Create Project
    # FIX: Use correct model field names for Project
    proj = models.Project(
        project_id=payload.project_id,
        project_name=payload.project_name,
        business_unit_id=payload.business_unit_id,
        project_description=payload.project_description,
        plan_start_date=payload.plan_start_date,
        plan_end_date=payload.plan_end_date,
        delivery_manager_id=dm_employee.EmployeeId, # Use validated EmployeeId
        createdby=current_user.user_id, # FIX: Use correct user field: user_id
        entitystatus=payload.entitystatus,
        createdat=datetime.utcnow(),
    )
    
    db.add(proj)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        if 'Duplicate entry' in str(e):
             # FIX: Use correct project field: project_id
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Project with ID {payload.project_id} already exists.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create project due to a database error.")

    db.refresh(proj)
    # FIX: Use correct project and user field names
    crud.audit_log(db, 'Project', proj.project_id, 'Create', changed_by=current_user.user_id)

    # 5. Return the ORM object, let Pydantic handle the rest
    return crud.get_project_read_model(db, proj.project_id, current_user, proj=proj)


# ------------------------- GET PROJECT BY ID -------------------------

@router.get("/{id}", response_model=schemas.ProjectRead, summary="Get Project details by Project ID")
def get_project_by_id(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    current_employee = get_employee_by_user(db, current_user)

    # 1. Fetch the Project
    # FIX: Use correct project field name: project_id
    project = db.query(models.Project).filter(
        models.Project.project_id == id,
        models.Project.entitystatus != "Archived"
    ).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or archived")

    # 2. Permission Check: Access control logic
    is_allowed = False
    
    # ADMIN check
    if role_name == Role.ADMIN:
        is_allowed = True
    
    # BU HEAD check
    # FIX: Use correct project field name: business_unit_id
    elif role_name == Role.BU_HEAD and project.business_unit_id == user_bu_id:
        is_allowed = True
        
    # Project Manager/Delivery Manager/Team Member Check
    else:
        # Check if the user is the project's Delivery Manager
        # FIX: Use correct project field name: delivery_manager_id
        if project.delivery_manager_id == current_employee.EmployeeId:
            is_allowed = True
        
        # Check if the user is assigned to the project's team (ProjectTeam model)
        if not is_allowed:
            # Assuming ProjectTeam uses project_id and EmployeeId
            is_member = db.query(models.ProjectTeam).filter(
                models.ProjectTeam.ProjectId == id,
                models.ProjectTeam.EmployeeId == current_employee.EmployeeId
            ).first()
            if is_member:
                is_allowed = True
            
    if not is_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this project.")

    # 3. Return the ORM object
    return crud.get_project_read_model(db, project.project_id, current_user, proj=project)


# ------------------------- GET ALL PROJECTS -------------------------

@router.get("/", response_model=List[schemas.ProjectRead], summary="Get all projects")
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    query = db.query(models.Project)
    
    # Non-admins only see projects in their BU
    if role_name != Role.ADMIN:
        # Filter projects by the user's BU
        # FIX: Use correct project field name: business_unit_id
        query = query.filter(models.Project.business_unit_id == user_bu_id)
    
    projects = query.all()

    # Prepare response: Use a helper to correctly build the complex ProjectRead model for each project
    response = [
        # FIX: Use correct project field name: project_id
        crud.get_project_read_model(db, proj.project_id, current_user, proj=proj)
        for proj in projects
    ]

    return response

# ------------------------- UPDATE PROJECT -------------------------

@router.put("/{id}", response_model=schemas.ProjectRead, summary="Update project")
def update_project(
    id: str,
    payload: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # FIX: Use correct project field name: project_id
    proj = db.query(models.Project).filter(models.Project.project_id == id).first()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    current_employee = get_employee_by_user(db, current_user)
    
    # Permission Check
    is_authorized = False
    if role_name == Role.ADMIN:
        is_authorized = True
    # FIX: Use correct project field name: business_unit_id
    elif role_name == Role.BU_HEAD and proj.business_unit_id == user_bu_id:
        is_authorized = True
    # FIX: Use correct project field name: delivery_manager_id
    elif current_employee.EmployeeId == proj.delivery_manager_id: 
        is_authorized = True
        
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied. You must be the ADMIN, BU HEAD of the project's BU, or the Delivery Manager.")

    # Update Delivery Manager if provided in payload
    # FIX: Use correct payload field name: delivery_manager_id
    if payload.delivery_manager_id:
        dm_employee = db.query(models.Employee).filter(
            models.Employee.EmployeeId == payload.delivery_manager_id.strip().upper()
        ).first()
        if not dm_employee:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New Delivery Manager EmployeeId not found.")
        # FIX: Use correct project field name: delivery_manager_id
        proj.delivery_manager_id = dm_employee.EmployeeId
    
    # Update other fields from payload
    update_data = payload.model_dump(exclude_unset=True) 

    update_data['updatedat'] = datetime.utcnow() # FIX: Use updatedat field
    
    for field, value in update_data.items():
        # FIX: Check for the correct field name
        if field not in ["delivery_manager_id"] and value is not None:
            setattr(proj, field, value)

    db.commit()
    db.refresh(proj)
    # FIX: Use correct project and user field names
    crud.audit_log(db, 'Project', proj.project_id, 'Update', changed_by=current_user.user_id)
    
    # Return the complex read model
    return crud.get_project_read_model(db, proj.project_id, current_user, proj=proj)

# ------------------------- ARCHIVE PROJECT -------------------------

@router.patch("/{id}/archive", response_model=schemas.ProjectRead, summary="Archive project")
def archive_project(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # FIX: Use correct project field name: project_id
    proj = db.query(models.Project).filter(models.Project.project_id == id).first()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    # Permission Check
    if role_name not in [Role.ADMIN, Role.BU_HEAD]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied. Only ADMIN or BU HEAD can archive projects.")
    
    # BU HEAD restriction
    # FIX: Use correct project field name: business_unit_id
    if role_name == Role.BU_HEAD and proj.business_unit_id != user_bu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="BU HEAD can only archive projects within their own BU.")


    proj.entitystatus = "Archived" # FIX: Use correct field: entitystatus
    proj.updatedat = datetime.utcnow() # FIX: Use correct field: updatedat
    db.commit()
    db.refresh(proj)
    # FIX: Use correct project and user field names
    crud.audit_log(db, 'Project', proj.project_id, 'Archive', changed_by=current_user.user_id)
    
    # Return the complex read model
    return crud.get_project_read_model(db, proj.project_id, current_user, proj=proj)