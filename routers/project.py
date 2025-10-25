<<<<<<< HEAD
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
=======
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from typing import List, Optional
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy import or_
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
from datetime import datetime
import logging
from .deliverable import get_current_user_from_cookie
from fastapi.security import OAuth2PasswordBearer
from main.models import *
router = APIRouter()
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from main import models, schemas
from .deliverable import get_db, get_current_user_from_cookie


SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

logger = logging.getLogger("uvicorn.error")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
<<<<<<< HEAD
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
=======
        if username is None:
            logger.debug("Token payload missing 'sub'")
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_from_cookie(
    access_token: Optional[str] = Cookie(None),
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")
    username = decode_token_and_get_username(access_token)
    user = db.query(models.User).filter(models.User.userName == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

@router.post("/", response_model=schemas.ProjectRead, summary="Create a new project")
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
<<<<<<< HEAD
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
=======
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.ADMIN]:
        raise HTTPException(status_code=403, detail="You do not have permission to create a project")

    if payload.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot create projects outside your Business Unit")

    if not db.query(models.BusinessUnit).filter(models.BusinessUnit.BUId == payload.BUId).first():
        raise HTTPException(status_code=400, detail="Invalid BUId")

    existing_project = db.query(models.Project).filter(models.Project.ProjectId == payload.ProjectId).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="Project already exists")

    delivery_manager = db.query(models.User).filter(
        or_(
            models.User.UserId == payload.DeliveryManager,
            models.User.userName == payload.DeliveryManager
        )
    ).first()

    if not delivery_manager:
        raise HTTPException(status_code=404, detail="Delivery Manager not found")

    project_data = payload.dict(exclude={"DeliveryManager"})
    obj = models.Project(**project_data)
    obj.DeliveryManagerId = delivery_manager.UserId
    obj.CreatedById = current_user.UserId
    obj.CreatedAt = datetime.utcnow()
    obj.EntityStatus = "Active"

    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'Project', obj.ProjectId, 'Create')
    return obj






@router.get("/", response_model=List[schemas.ProjectRead], summary="List projects")
def list_projects(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    disallowed_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.REVIEWER]
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="You do not have access to view projects")

    query = db.query(models.Project)

    if current_user.role_name == models.Role.BU_HEAD:
        query = query.filter(models.Project.BUId == current_user.BUId)
    elif current_user.role_name == models.Role.DELIVERY_MANAGER:
        employee = db.query(models.Employee).filter(models.Employee.UserId == current_user.UserId).first()
        if not employee:
            return []
        query = query.filter(
            models.Project.BUId == current_user.BUId,
            models.Project.DeliveryManagerId == current_user.UserId  # Since DeliveryManagerId stores UserId
        )
    elif current_user.role_name == models.Role.PROJECT_MANAGER:
        query = query.filter(models.Project.BUId == current_user.BUId)

    projects = query.offset(offset).limit(limit).all()

    response = []
    for proj in projects:
        delivery_manager_data = None
        if proj.DeliveryManagerId:
            # DeliveryManagerId stores UserId, so first get User
            user = db.query(models.User).filter(models.User.UserId == proj.DeliveryManagerId).first()
            if user and user.employee:
                # user.employee is the linked Employee object
                delivery_manager_data = {
                    "EmployeeId": user.employee.EmployeeId,
                    "FullName": f"{user.fullName}",
                    "Email": user.employee.Email,
                    "BUId": user.employee.BUId,
                    "HolidayCalendarId": user.employee.HolidayCalendarId if hasattr(user.employee, "HolidayCalendarId") else None,
                    "Status": user.employee.EntityStatus,
                }

        created_by_data = None
        if proj.CreatedById:
            created_by = db.query(models.User).filter(models.User.UserId == proj.CreatedById).first()
            if created_by:
                created_by_data = {
                    "UserId": created_by.UserId,
                    "userName": created_by.userName,
                    "fullName": created_by.fullName,
                    "emailID": created_by.emailID,
                    "BUId": created_by.BUId,
                    "RoleId": created_by.RoleId,
                }

        deliverables_data = [
            {
                "DeliverableId": d.DeliverableId,
                "PlannedStartDate": d.PlannedStartDate,
                "PlannedEndDate": d.PlannedEndDate,
            }
            for d in proj.deliverables
        ]

        response.append(
            schemas.ProjectRead(
                ProjectId=proj.ProjectId,
                ProjectName=proj.ProjectName,
                BUId=proj.BUId,
                PlannedStartDate=proj.PlannedStartDate,
                PlannedEndDate=proj.PlannedEndDate,
                DeliveryManager=delivery_manager_data,
                CreatedBy=created_by_data,
                deliverables=deliverables_data,
                EntityStatus=proj.EntityStatus,
                CreatedAt=proj.CreatedAt,
            )
        )

    return response



@router.get("/{item_id}", response_model=schemas.ProjectRead, summary="Get project by ID")
def get_project(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.Project).filter(models.Project.ProjectId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role_name in [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.REVIEWER]:
        raise HTTPException(status_code=403, detail="You do not have permission to view this project")

    if current_user.role_name == models.Role.BU_HEAD and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="BU Head can only access their BU projects")

    if current_user.role_name == models.Role.DELIVERY_MANAGER and (
        obj.BUId != current_user.BUId or obj.DeliveryManagerId != current_user.UserId
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this project")

    if current_user.role_name == models.Role.PROJECT_MANAGER and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="PMs can only view projects within their BU")

    return obj


@router.put("/{item_id}", response_model=schemas.ProjectRead, summary="Update a project")
def update_project(
    item_id: str,
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to update projects")

    obj = db.query(models.Project).filter(models.Project.ProjectId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role_name == models.Role.PROJECT_MANAGER and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update projects outside your BU")

    exclude_fields = {"CreatedById", "CreatedAt", "EntityStatus"}
    for k, v in payload.dict(exclude=exclude_fields).items():
        setattr(obj, k, v)

    obj.UpdatedAt = datetime.utcnow()

    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'Project', obj.ProjectId, 'Update', changed_by=current_user.userName)
    return obj


@router.patch("/{item_id}/archive", summary="Archive a project")
def archive_project(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to archive projects")

    obj = db.query(models.Project).filter(models.Project.ProjectId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role_name == models.Role.PROJECT_MANAGER and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot archive projects outside your BU")

    obj.EntityStatus = "Archived"
    obj.UpdatedAt = datetime.utcnow()
    db.commit()

    crud.audit_log(db, 'Project', obj.ProjectId, 'Archive', changed_by=current_user.userName)

    return {"status": "archived", "project_id": obj.ProjectId}
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
