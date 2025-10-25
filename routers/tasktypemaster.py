from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()

SECRET_KEY = "super-secret-key"  # replace with env var in prod
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


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


@router.post("/", response_model=schemas.TaskTypeMasterRead, summary="Add new Task Type record.")
def create_item(
    payload: schemas.TaskTypeMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

    if db.query(models.TaskTypeMaster).filter_by(TaskTypeId=payload.TaskTypeId).first():
        raise HTTPException(status_code=400, detail="TaskTypeId already exists")

    if db.query(models.TaskTypeMaster).filter(models.TaskTypeMaster.TaskTypeName.ilike(payload.TaskTypeName)).first():
        raise HTTPException(status_code=400, detail="TaskTypeName already exists")

    obj = models.TaskTypeMaster(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

<<<<<<< HEAD
    crud.audit_log(db, 'TaskTypeMaster', obj.TaskTypeId, 'Create',changed_by=current_user.UserId)
=======
    crud.audit_log(db, 'TaskTypeMaster', obj.TaskTypeId, 'Create')
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj


@router.get("/", response_model=List[schemas.TaskTypeMasterRead], summary="Get list of Task Type records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    disallowed_roles = ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Can't view details")

    query = db.query(models.TaskTypeMaster)
    return query.offset(offset).limit(limit).all()


<<<<<<< HEAD
@router.get("/{id}", response_model=schemas.TaskTypeMasterRead, summary="Get Task Type by ID.")
def get_item(
    id: str,
=======
@router.get("/{item_id}", response_model=schemas.TaskTypeMasterRead, summary="Get Task Type by ID.")
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
    obj = db.query(models.TaskTypeMaster).get(id)
=======
    obj = db.query(models.TaskTypeMaster).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Task Type not found")
    return obj


<<<<<<< HEAD
@router.put("/{id}", response_model=schemas.TaskTypeMasterRead, summary="Update Task Type record.")
def update_item(
    id: str,
=======
@router.put("/{item_id}", response_model=schemas.TaskTypeMasterRead, summary="Update Task Type record.")
def update_item(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    payload: schemas.TaskTypeMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    allowed_roles = [models.Role.ADMIN, models.Role.PROJECT_MANAGER]
    check_permission(current_user, allowed_roles)

<<<<<<< HEAD
    obj = db.query(models.TaskTypeMaster).get(id)
=======
    obj = db.query(models.TaskTypeMaster).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Task Type not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)

<<<<<<< HEAD
    crud.audit_log(db, 'TaskTypeMaster', obj.TaskTypeId, 'Update', changed_by=current_user.UserId)
    return obj


@router.patch("/{id}", response_model=schemas.TaskTypeMasterRead, summary="Partially update a Task Type Master record.")
def update_task_type_master_partial(
    id: str,
    payload: schemas.TaskTypeMasterUpdate, # Update schema
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)

    # 1. Permission Check
    if role_name != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only ADMIN is authorized to modify Task Type Master records.")

    # 2. Fetch the record
    obj = db.query(models.TaskTypeMaster).filter(
        models.TaskTypeMaster.TaskTypeId == id,
        models.TaskTypeMaster.EntityStatus != "Archived"
    ).first()

    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task Type not found or archived")

    # 3. Perform Update
    update_data = payload.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(obj, key, value)

    obj.UpdatedAt = now()
    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    crud.audit_log(
        db,
        'TaskTypeMaster',
        obj.TaskTypeId,
        'Update (Partial)',
        changed_by=current_user.UserId
    )
=======
    crud.audit_log(db, 'TaskTypeMaster', obj.TaskTypeId, 'Update', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    return obj
