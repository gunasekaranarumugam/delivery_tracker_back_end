from fastapi import APIRouter, Depends, HTTPException, Cookie, Request
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from jose import jwt, JWTError

from main import models, schemas, crud
from main.database import get_db
from fastapi.security import OAuth2PasswordBearer
from main.models import Role  # constants class

router = APIRouter()

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

# ------------------------- AUTH HELPERS -------------------------

def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def attach_employee_and_role(user, db: Session, employee_id: str):
    if not employee_id:
        raise HTTPException(status_code=400, detail="EmployeeId not provided")

    employee_id_clean = employee_id.strip().upper()
    employee = db.query(models.Employee).filter(
        func.upper(models.Employee.EmployeeId) == employee_id_clean
    ).first()
    if not employee:
        raise HTTPException(status_code=400, detail=f"Employee '{employee_id_clean}' not found")

    user.employee = employee
    if not employee.RoleId:
        raise HTTPException(status_code=400, detail=f"Role not assigned to employee '{employee_id_clean}'")

    role = db.query(models.RoleMaster).filter(
        func.upper(models.RoleMaster.RoleId) == employee.RoleId.strip().upper()
    ).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{employee.RoleId}' not found for employee '{employee_id_clean}'")

    user.role = role
    return user



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

# ------------------------- CREATE PROJECT -------------------------

@router.post("/", response_model=schemas.ProjectRead, summary="Create a new project")
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    emp = db.query(models.Employee).filter(models.Employee.Email == current_user.emailID).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Your employee record not found")
    if not emp.RoleId:
        raise HTTPException(status_code=403, detail="Role not assigned to your employee")

    role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleId == emp.RoleId).first()
    if role.RoleName not in [Role.BU_HEAD, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Only non-admins are restricted by BU
    if role.RoleName != Role.ADMIN and payload.BUId != emp.BUId:
        raise HTTPException(status_code=403, detail="Cannot create project outside your BU")

    if not payload.DeliveryManager:
        raise HTTPException(status_code=400, detail="DeliveryManager EmployeeId not provided")

    dm_user = attach_employee_and_role(models.User(), db, payload.DeliveryManager)

    proj = models.Project(
        ProjectId=payload.ProjectId,
        ProjectName=payload.ProjectName,
        BUId=payload.BUId,
        PlannedStartDate=payload.PlannedStartDate,
        PlannedEndDate=payload.PlannedEndDate,
        DeliveryManagerId=dm_user.employee.EmployeeId,
        CreatedById=current_user.UserId,
        CreatedAt=datetime.utcnow(),
        EntityStatus="Active"
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    crud.audit_log(db, 'Project', proj.ProjectId, 'Create', changed_by=current_user.UserId)

    delivery_manager_data = {
        "EmployeeId": dm_user.employee.EmployeeId,
        "FullName": f"{dm_user.employee.FirstName} {dm_user.employee.LastName}",
        "Email": dm_user.employee.Email,
        "BUId": dm_user.employee.BUId,
        "Status": dm_user.employee.EntityStatus,
        "RoleName": dm_user.role.RoleName
    }
    created_by_data = {
        "UserId": current_user.UserId,
        "userName": current_user.userName,
        "fullName": f"{emp.FirstName} {emp.LastName}",
        "emailID": current_user.emailID,
        "BUId": emp.BUId,
        "RoleName": role.RoleName,
        "RoleId": role.RoleId,
    }

    return schemas.ProjectRead(
        ProjectId=proj.ProjectId,
        ProjectName=proj.ProjectName,
        BUId=proj.BUId,
        PlannedStartDate=proj.PlannedStartDate,
        PlannedEndDate=proj.PlannedEndDate,
        DeliveryManager=delivery_manager_data,
        CreatedBy=created_by_data,
        deliverables=[],
        EntityStatus=proj.EntityStatus,
        CreatedAt=proj.CreatedAt,
    )

# ✅ GET - Project by ID
@router.get("/{id}", response_model=schemas.ProjectRead, summary="Get Project details by Project ID")
def get_project_by_id(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)

    # 1. Fetch the Project
    project = db.query(models.Project).filter(
        models.Project.ProjectId == id,
        models.Project.EntityStatus != "Archived"
    ).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or archived")

    # 2. Permission Check: Access control logic
    
    # Who can view a project?
    # - ADMIN: Always
    # - BU HEAD: Projects in their BU
    # - Project Manager/Delivery Manager: Projects they are assigned to
    # - Other Roles: Typically restricted or only allowed for projects they are actively on (this requires checking the ProjectTeam model)
    
    allowed_roles = ["ADMIN", "BU HEAD", "PROJECT MANAGER", "DELIVERY MANAGER"]
    
    if role_name in allowed_roles:
        if role_name == "ADMIN":
            return project # Admin can view any project

        if role_name == "BU HEAD":
            # Check if the project belongs to the user's BU
            if project.BUId == user_bu_id:
                return project
            else:
                # BU HEAD can only see projects in their own BU
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view projects in your Business Unit")

        # For PM/DM, we need to check the ProjectTeam assignments.
        # This requires fetching the current user's Employee ID first.
        current_employee = db.query(models.Employee).filter(models.Employee.Email == current_user.emailID).first()
        if current_employee and current_employee.EmployeeId:
            # Check if the user is assigned to the project's team
            is_member = db.query(models.ProjectTeam).filter(
                models.ProjectTeam.ProjectId == id,
                models.ProjectTeam.EmployeeId == current_employee.EmployeeId
            ).first()
            if is_member:
                return project
            
    # If the user is none of the above (or PM/DM but not on the team), deny access.
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this project.")

    
@router.get("/", response_model=list[schemas.ProjectRead], summary="Get all projects")
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Get the employee and role for permission check
    emp = db.query(models.Employee).filter(models.Employee.Email == current_user.emailID).first()
    if not emp:
        raise HTTPException(status_code=403, detail="Employee record not found")
    
    role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleId == emp.RoleId).first()
    if not role:
        raise HTTPException(status_code=403, detail="Role not assigned to employee")
    
    # Non-admins only see projects in their BU
    if role.RoleName != "ADMIN":
        projects = db.query(models.Project).filter(models.Project.BUId == emp.BUId).all()
    else:
        projects = db.query(models.Project).all()  # Admin can see all

    # Prepare response
    response = []
    for proj in projects:
        dm_emp = db.query(models.Employee).filter(models.Employee.EmployeeId == proj.DeliveryManagerId).first()
        dm_role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleId == dm_emp.RoleId).first() if dm_emp else None

        delivery_manager_data = {
            "EmployeeId": dm_emp.EmployeeId if dm_emp else None,
            "FullName": f"{dm_emp.FirstName} {dm_emp.LastName}" if dm_emp else None,
            "Email": dm_emp.Email if dm_emp else None,
            "BUId": dm_emp.BUId if dm_emp else None,
            "Status": dm_emp.EntityStatus if dm_emp else None,
            "RoleId": dm_role.RoleId if dm_role else None,
            "RoleName": dm_role.RoleName if dm_role else None
        }

        created_by_emp = db.query(models.Employee).filter(models.Employee.Email == current_user.emailID).first()
        created_by_role = role

        created_by_data = {
            "UserId": current_user.UserId,
            "userName": current_user.userName,
            "fullName": f"{created_by_emp.FirstName} {created_by_emp.LastName}" if created_by_emp else None,
            "emailID": current_user.emailID,
            "BUId": created_by_emp.BUId if created_by_emp else None,
            "RoleId": created_by_role.RoleId,
            "RoleName": created_by_role.RoleName
        }

        response.append(schemas.ProjectRead(
            ProjectId=proj.ProjectId,
            ProjectName=proj.ProjectName,
            BUId=proj.BUId,
            PlannedStartDate=proj.PlannedStartDate,
            PlannedEndDate=proj.PlannedEndDate,
            DeliveryManager=delivery_manager_data,
            CreatedBy=created_by_data,
            deliverables=[],  # include deliverables if needed
            EntityStatus=proj.EntityStatus,
            CreatedAt=proj.CreatedAt,
        ))

    return response

# ------------------------- UPDATE PROJECT -------------------------

@router.put("/{id}", response_model=schemas.ProjectRead, summary="Update project")
def update_project(
    id: str,
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    proj = db.query(models.Project).filter(models.Project.ProjectId == id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    emp = db.query(models.Employee).filter(models.Employee.Email == current_user.emailID).first()
    role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleId == emp.RoleId).first()
    if role.RoleName not in [Role.ADMIN, Role.BU_HEAD, Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Permission denied")

    if payload.DeliveryManager:
        dm_user = attach_employee_and_role(models.User(), db, payload.DeliveryManager)
        proj.DeliveryManagerId = dm_user.employee.EmployeeId

    for field, value in payload.dict(exclude={"DeliveryManager"}).items():
        if value is not None:
            setattr(proj, field, value)

    db.commit()
    db.refresh(proj)
    crud.audit_log(db, 'Project', proj.ProjectId, 'Update', changed_by=current_user.UserId)
    return proj

# ------------------------- ARCHIVE PROJECT -------------------------

@router.patch("/{id}/archive", response_model=schemas.ProjectRead, summary="Archive project")
def archive_project(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    proj = db.query(models.Project).filter(models.Project.ProjectId == id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    emp = db.query(models.Employee).filter(models.Employee.Email == current_user.emailID).first()
    role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleId == emp.RoleId).first()
    if role.RoleName not in [Role.ADMIN, Role.BU_HEAD]:
        raise HTTPException(status_code=403, detail="Permission denied")

    proj.EntityStatus = "Archived"
    db.commit()
    db.refresh(proj)
    crud.audit_log(db, 'Project', proj.ProjectId, 'Archive', changed_by=current_user.UserId)
    return proj
