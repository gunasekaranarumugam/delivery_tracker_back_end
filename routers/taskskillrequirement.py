from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

SECRET_KEY = "super-secret-key"  # Use environment variables in production
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


@router.post("/", response_model=schemas.TaskSkillRequirementRead, summary="Add new Task Skill Requirement record.")
def create_item(
    payload: schemas.TaskSkillRequirementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

    existing_id = db.query(models.TaskSkillRequirement).filter_by(TaskSkillRequirementId=payload.TaskSkillRequirementId).first()
    if existing_id:
        raise HTTPException(status_code=400, detail="TaskSkillRequirementId already exists")

    task = db.query(models.Task).filter_by(TaskId=payload.TaskId).first()
    if not task:
        raise HTTPException(status_code=400, detail="Invalid TaskId")

    skill = db.query(models.SkillMaster).filter_by(SkillId=payload.SkillId).first()
    if not skill:
        raise HTTPException(status_code=400, detail="Invalid SkillId")

    obj = models.TaskSkillRequirement(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

<<<<<<< HEAD
    crud.audit_log(db, 'TaskSkillRequirement', obj.TaskSkillRequirementId, 'Create', changed_by=current_user.UserId)
=======
    crud.audit_log(db, 'TaskSkillRequirement', obj.TaskSkillRequirementId, 'Create', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj


@router.get("/", response_model=List[schemas.TaskSkillRequirementRead], summary="Get list of Task Skill Requirement records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    # Restrict viewing to certain roles
    disallowed_roles = ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

    query = db.query(models.TaskSkillRequirement)
    return query.offset(offset).limit(limit).all()


<<<<<<< HEAD
@router.get("/{id}", response_model=schemas.TaskSkillRequirementRead, summary="Get Task Skill Requirement by ID.")
def get_item(
    id: str,
=======
@router.get("/{item_id}", response_model=schemas.TaskSkillRequirementRead, summary="Get Task Skill Requirement by ID.")
def get_item(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    disallowed_roles = ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

<<<<<<< HEAD
    obj = db.query(models.TaskSkillRequirement).get(id)
=======
    obj = db.query(models.TaskSkillRequirement).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Task Skill Requirement not found")
    return obj


<<<<<<< HEAD
@router.put("/{id}", response_model=schemas.TaskSkillRequirementRead, summary="Update Task Skill Requirement record.")
def update_item(
    id: str,
=======
@router.put("/{item_id}", response_model=schemas.TaskSkillRequirementRead, summary="Update Task Skill Requirement record.")
def update_item(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    payload: schemas.TaskSkillRequirementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

<<<<<<< HEAD
    obj = db.query(models.TaskSkillRequirement).get(id)
=======
    obj = db.query(models.TaskSkillRequirement).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Task Skill Requirement not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

<<<<<<< HEAD
    crud.audit_log(db, 'TaskSkillRequirement', obj.TaskSkillRequirementId, 'Update', changed_by=current_user.UserId)
    return obj


@router.patch("/{id}", response_model=schemas.TaskSkillRequirementRead, summary="Partially update a Task Skill Requirement record.")
def update_task_skill_requirement_partial(
    id: str,
    payload: schemas.TaskSkillRequirementUpdate, # Schema with Optional fields for partial update
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    
    # 1. Permission Check
    # Only ADMIN and BU HEAD are usually authorized to modify skill requirements.
    if role_name not in ["ADMIN", "BU HEAD"]: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Only ADMIN or BU HEAD is authorized to modify Task Skill Requirement records.")

    # 2. Fetch the TaskSkillRequirement record
    obj = db.query(models.TaskSkillRequirement).filter(
        models.TaskSkillRequirement.TaskSkillRequirementId == id,
        models.TaskSkillRequirement.EntityStatus != "Archived" # Assuming EntityStatus exists
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Skill Requirement not found or archived")

    # 3. Perform Update
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    # Assuming the model has an UpdatedAt column
    if hasattr(obj, 'UpdatedAt'):
        obj.UpdatedAt = now() 
        
    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    crud.audit_log(
        db, 
        'TaskSkillRequirement', 
        obj.TaskSkillRequirementId, 
        'Update (Partial)', 
        changed_by=current_user.UserId 
    )
    
=======
    crud.audit_log(db, 'TaskSkillRequirement', obj.TaskSkillRequirementId, 'Update', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj
