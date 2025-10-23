from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db

router = APIRouter()

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

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


@router.post("/", response_model=schemas.DeliverableRead, summary="Add new Deliverable")
def create_deliverable(
    payload: schemas.DeliverableCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    allowed_roles = [models.Role.PROJECT_MANAGER, models.Role.DELIVERY_MANAGER, models.Role.ADMIN]
    if current_user.role_name not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to create deliverables")

    existing = db.query(models.Deliverable).filter_by(DeliverableId=payload.DeliverableId).first()
    if existing:
        raise HTTPException(status_code=400, detail="DeliverableId already exists")

    # BU restriction
    if current_user.role_name in [models.Role.PROJECT_MANAGER, models.Role.DELIVERY_MANAGER]:
        if not current_user.BUId or payload.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Cannot create deliverables outside your Business Unit")

    # FK checks
    if not db.query(models.Project).filter_by(ProjectId=payload.ProjectId).first():
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.ProjectManagerId:
        if not db.query(models.User).filter_by(UserId=payload.ProjectManagerId).first():
            raise HTTPException(status_code=404, detail="Project Manager not found")

    # Create
    deliverable = models.Deliverable(**payload.dict())
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)

    crud.audit_log(db, 'Deliverable', deliverable.DeliverableId, 'Create') 
    return deliverable


@router.get("/", response_model=List[schemas.DeliverableRead], summary="List deliverables")
def list_deliverables(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    disallowed_roles = [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.REVIEWER]
    if current_user.role_name in disallowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to view deliverables")

    query = db.query(models.Deliverable)

    # BU filter (except for BU Head and Admin)
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.ADMIN]:
        query = query.filter(models.Deliverable.BUId == current_user.BUId)

    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.DeliverableRead, summary="Get deliverable by ID")
def get_deliverable(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.Deliverable).filter_by(DeliverableId=item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if current_user.role_name in [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.REVIEWER]:
        raise HTTPException(status_code=403, detail="Not authorized to view this deliverable")

    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.ADMIN] and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Not authorized to view this deliverable")

    return obj


@router.put("/{item_id}", response_model=schemas.DeliverableRead, summary="Update Deliverable")
def update_deliverable(
    item_id: str,
    payload: schemas.DeliverableCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER, models.Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to update deliverables")

    obj = db.query(models.Deliverable).filter_by(DeliverableId=item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if current_user.role_name == models.Role.PROJECT_MANAGER and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update deliverables outside your BU")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    obj.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'Deliverable', obj.DeliverableId, 'Update', changed_by=current_user.userName)
    return obj


@router.patch("/{item_id}/archive", summary="Archive Deliverable")
def archive_deliverable(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [models.Role.BU_HEAD, models.Role.PROJECT_MANAGER, models.Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to archive deliverables")

    obj = db.query(models.Deliverable).filter_by(DeliverableId=item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if current_user.role_name == models.Role.PROJECT_MANAGER and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot archive deliverables outside your BU")

    obj.EntityStatus = "Archived"
    obj.UpdatedAt = datetime.utcnow()
    db.commit()

    crud.audit_log(db, 'Deliverable', obj.DeliverableId, 'Archive', changed_by=current_user.userName)
    return {"status": "archived"}
