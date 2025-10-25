from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, status
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from jose import jwt, JWTError
from datetime import datetime
import logging
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()

SECRET_KEY = "super-secret-key"  # Use env var in production
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

logger = logging.getLogger("uvicorn.error")

def decode_token_and_get_username(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.debug("Token payload missing 'sub'")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return username
    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user_from_cookie(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> models.User:
    if not access_token:
        logger.debug("Access token cookie is missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")

    username = decode_token_and_get_username(access_token)
    user = db.query(models.User).filter(models.User.userName == username).first()
    if not user:
        logger.debug(f"User not found for username: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def check_permission(current_user: models.User, allowed_roles: List[str]):
    if current_user.role_name not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

@router.post("/", response_model=schemas.ReviewDiscussionThreadRead, summary="Add new Review Thread record.")
def create_item(
    payload: schemas.ReviewDiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.PROJECT_MANAGER])

    existing_thread = db.query(models.ReviewDiscussionThread).filter_by(ThreadId=payload.ThreadId).first()
    if existing_thread:
        raise HTTPException(status_code=400, detail="ThreadId already exists")

    review = db.query(models.Review).filter_by(ReviewId=payload.ReviewId).first()
    if not review:
        raise HTTPException(status_code=400, detail="Invalid ReviewId")

    obj = models.ReviewDiscussionThread(**payload.dict())
    obj.CreatedById = current_user.UserId
    obj.CreatedAt = datetime.utcnow()
    obj.EntityStatus = "Active"

    db.add(obj)
    db.commit()
    db.refresh(obj)
    crud.audit_log(db, 'ReviewDiscussionThread', getattr(obj, 'ThreadId'), 'Create',changed_by=current_user.UserId)
    return obj

@router.get("/", response_model=List[schemas.ReviewDiscussionThreadRead], summary="Get list of Review Thread records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    q = db.query(models.ReviewDiscussionThread).filter(models.ReviewDiscussionThread.EntityStatus != "Archived")
    return q.offset(offset).limit(limit).all()

@router.get("/{id}", response_model=schemas.ReviewDiscussionThreadRead, summary="Get Review Thread by ID.")
def get_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.ReviewDiscussionThread).filter(
        models.ReviewDiscussionThread.ThreadId == id,
        models.ReviewDiscussionThread.EntityStatus != "Archived"
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Review Thread not found")
    return obj

@router.put("/{id}", response_model=schemas.ReviewDiscussionThreadRead, summary="Update Review Thread record.")
def update_item(
    id: str,
    payload: schemas.ReviewDiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    check_permission(current_user, [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.PROJECT_MANAGER])

    obj = db.query(models.ReviewDiscussionThread).filter(
        models.ReviewDiscussionThread.ThreadId == id,
        models.ReviewDiscussionThread.EntityStatus != "Archived"
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Review Thread not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    obj.UpdatedAt = datetime.utcnow()
    obj.UpdatedById = current_user.UserId

    db.commit()
    db.refresh(obj)
    crud.audit_log(db, 'ReviewDiscussionThread', getattr(obj, 'ThreadId'), 'Update', changed_by=current_user.UserId)
    return obj

@router.patch("/{id}", response_model=schemas.ReviewDiscussionThreadRead, summary="Partially update a Review Discussion Thread record.")
def update_discussion_thread_partial(
    id: str,
    payload: schemas.ReviewDiscussionThreadUpdate, # Schema with Optional fields for partial update
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    # 1. Fetch the ReviewDiscussionThread record
    obj = db.query(models.ReviewDiscussionThread).filter(
        models.ReviewDiscussionThread.DiscussionId == id, # Assuming the primary key is DiscussionId
        models.ReviewDiscussionThread.EntityStatus != "Archived" # Assuming EntityStatus exists
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion Thread not found or archived")

    # 2. Permission Check
    
    # Check 2a: Only ADMIN can modify any thread.
    if role_name == "ADMIN":
        pass # Admin authorized

    # Check 2b: The creator/owner of the thread can modify it (e.g., fix a typo).
    elif hasattr(obj, 'CreatedById') and obj.CreatedById == current_user.UserId:
        pass # Creator authorized
        
    # Check 2c: Project Manager or BU Head might be allowed to modify threads in their area.
    # This check would be complex, requiring linking the thread back to a project/review.
    # For simplicity, we restrict to Admin or Creator.
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to modify this discussion thread. Only the creator or ADMIN can update.")

    # 3. Perform Update
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    # Set UpdatedAt timestamp
    if hasattr(obj, 'UpdatedAt'):
        obj.UpdatedAt = now() 
        
    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    crud.audit_log(
        db, 
        'ReviewDiscussionThread', 
        obj.DiscussionId, 
        'Update (Partial)', 
        changed_by=current_user.UserId 
    )
    
    return obj
