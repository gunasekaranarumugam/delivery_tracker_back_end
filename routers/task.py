from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

SECRET_KEY = "super-secret-key"  # Move to env vars in production
ALGORITHM = "HS256"

def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except JWTError:
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action.")

@router.post("/", response_model=schemas.TaskRead, summary="Add new Task record.")
def create_item(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

    existing_task = db.query(models.Task).filter_by(TaskId=payload.TaskId).first()
    if existing_task:
        raise HTTPException(status_code=400, detail="TaskId already exists")

    deliverable = db.query(models.Deliverable).filter_by(DeliverableId=payload.DeliverableId).first()
    if not deliverable:
        raise HTTPException(status_code=400, detail="Invalid DeliverableId")

    # Validate Reviewer role if ReviewerId provided
    if payload.ReviewerId:
        reviewer = db.query(models.User).filter(models.User.UserId == payload.ReviewerId).first()
        if not reviewer:
            raise HTTPException(status_code=400, detail="Reviewer not found")
        if reviewer.role_name != models.Role.REVIEWER:
            raise HTTPException(status_code=400, detail="Assigned Reviewer must have REVIEWER role")

    obj = models.Task(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'Task', getattr(obj, 'TaskId'), 'Create',changed_by=current_user.UserId)

    return obj

"""@router.get("/", response_model=List[schemas.TaskRead], summary="Get list of Task records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Roles denied viewing tasks
    disallowed_roles = [models.Role.DELIVERY_MANAGER]
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to view task details")

    query = db.query(models.Task)

    if current_user.role_name == models.Role.PROJECT_MANAGER or current_user.role_name == models.Role.BU_HEAD:
        query = (
            query.join(models.Deliverable, models.Task.DeliverableId == models.Deliverable.DeliverableId)
            .filter(models.Deliverable.BUId == current_user.BUId)
        )
    # else Admin and other roles get all tasks

    return query.offset(offset).limit(limit).all()

@router.get("/{id}", response_model=schemas.TaskRead, summary="Get Task by ID.")
def get_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    disallowed_roles = [models.Role.DELIVERY_MANAGER]
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to view task details")

    query = db.query(models.Task)

    if current_user.role_name == models.Role.PROJECT_MANAGER or current_user.role_name == models.Role.BU_HEAD:
        query = (
            query.join(models.Deliverable, models.Task.DeliverableId == models.Deliverable.DeliverableId)
            .filter(models.Task.TaskId == id)
            .filter(models.Deliverable.BUId == current_user.BUId)
        )
        obj = query.first()
    else:
        obj = query.get(item_id)

    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")

    return obj"""

@router.get("/", response_model=List[schemas.TaskRead], summary="Get list of Task records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    disallowed_roles = [models.Role.DELIVERY_MANAGER]
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to view task details")

    query = db.query(models.Task)

    if current_user.role_name in [models.Role.PROJECT_MANAGER, models.Role.BU_HEAD]:
        query = (
            query.join(models.Deliverable, models.Task.DeliverableId == models.Deliverable.DeliverableId)
            .filter(models.Deliverable.BUId == current_user.BUId)
        )

    tasks = query.offset(offset).limit(limit).all()
    return tasks


@router.put("/{id}", response_model=schemas.TaskRead, summary="Update Task record.")
def update_item(
    id: str,
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

    obj = db.query(models.Task).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")

    # Validate Reviewer role if ReviewerId is updated
    if payload.ReviewerId:
        reviewer = db.query(models.User).filter(models.User.UserId == payload.ReviewerId).first()
        if not reviewer:
            raise HTTPException(status_code=400, detail="Reviewer not found")
        if reviewer.role_name != models.Role.REVIEWER:
            raise HTTPException(status_code=400, detail="Assigned Reviewer must have REVIEWER role")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'Task', getattr(obj, 'TaskId'), 'Update', changed_by=current_user.UserId)

    return obj

@router.patch("/{id}/archive", summary="Archive Task record.")
def archive_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

    obj = db.query(models.Task).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Task not found")

    obj.EntityStatus = "Archived"
    db.commit()

    crud.audit_log(db, 'Task', getattr(obj, 'TaskId'), 'Archive', changed_by=current_user.userName)

    return {"status": "archived"}


@router.get("/{id}", response_model=schemas.TaskRead, summary="Get Task details by Task ID")
def get_task_by_id(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)

    # 1. Fetch the Task
    task = db.query(models.Task).filter(
        models.Task.TaskId == id,
        models.Task.EntityStatus != "Archived"
    ).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or archived")

    # 2. Permission Check: Access control logic
    
    # Who can view a task?
    # - ADMIN/BU HEAD: Always
    # - The Employee the task is assigned to (Task.AssignedToId)
    # - The Project Manager (PM) of the task's Project (requires checking models.Project and models.ProjectTeam)

    # Check for High-Level Roles
    if role_name in ["ADMIN", "BU HEAD"]:
        return task
    
    # Check if the user is the assigned employee
    if task.AssignedToId == current_employee_id:
        return task

    # Check if the user is the Project Manager (PM) of the task's project
    if task.ProjectId:
        # Find the Project Manager for this task's project
        project_manager_role = db.query(models.RoleMaster).filter(models.RoleMaster.RoleName == "PROJECT MANAGER").first()
        
        if project_manager_role:
            # Check if the current user is a Project Manager assigned to this specific project
            is_project_manager = db.query(models.ProjectTeam).filter(
                models.ProjectTeam.ProjectId == task.ProjectId,
                models.ProjectTeam.EmployeeId == current_employee_id,
                models.ProjectTeam.RoleId == project_manager_role.RoleId
            ).first()

            if is_project_manager:
                return task

    # If none of the checks passed, deny access.
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this task.")