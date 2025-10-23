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


def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
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



@router.post("/", response_model=schemas.ProjectRead, summary="Create a new project")
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
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
