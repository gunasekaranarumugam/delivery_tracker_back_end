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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

SECRET_KEY = "super-secret-key"  # Use env var in production
ALGORITHM = "HS256"

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


def deny_roles(current_user: models.User, denied_roles: List[str]):
    if current_user.role_name in denied_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")


@router.post("/", response_model=schemas.ReviewDiscussionCommentRead, summary="Add new Review Comment record.")
def create_item(
    payload: schemas.ReviewDiscussionCommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only Admin and Project Manager can create comments
    check_permission(current_user, [models.Role.ADMIN, models.Role.PROJECT_MANAGER])

    existing_comment = db.query(models.ReviewDiscussionComment).filter_by(CommentId=payload.CommentId).first()
    if existing_comment:
        raise HTTPException(status_code=400, detail="CommentId already exists")

    thread = db.query(models.ReviewDiscussionThread).filter_by(ThreadId=payload.ThreadId).first()
    if not thread:
        raise HTTPException(status_code=400, detail="Invalid ThreadId")

    obj = models.ReviewDiscussionComment(**payload.dict())
    obj.CreatedById = current_user.UserId
    obj.CreatedAt = datetime.utcnow()
    obj.EntityStatus = "Active"

    db.add(obj)
    db.commit()
    db.refresh(obj)
    crud.audit_log(db, 'ReviewDiscussionComment', getattr(obj, 'CommentId'), 'Create')
    return obj


@router.get("/", response_model=List[schemas.ReviewDiscussionCommentRead], summary="Get list of Review Comment records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Deny access for certain roles
    deny_roles(current_user, [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.DELIVERY_MANAGER])

    q = db.query(models.ReviewDiscussionComment).filter(models.ReviewDiscussionComment.EntityStatus != "Archived")
    return q.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.ReviewDiscussionCommentRead, summary="Get Review Comment by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Deny access for certain roles
    deny_roles(current_user, [models.Role.DEVELOPER, models.Role.TEAM_MEMBER, models.Role.DELIVERY_MANAGER])

    obj = db.query(models.ReviewDiscussionComment).filter(
        models.ReviewDiscussionComment.CommentId == item_id,
        models.ReviewDiscussionComment.EntityStatus != "Archived"
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Review Comment not found")
    return obj


@router.put("/{item_id}", response_model=schemas.ReviewDiscussionCommentRead, summary="Update Review Comment record.")
def update_item(
    item_id: str,
    payload: schemas.ReviewDiscussionCommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only Admin and Project Manager can update comments
    check_permission(current_user, [models.Role.ADMIN, models.Role.PROJECT_MANAGER])

    obj = db.query(models.ReviewDiscussionComment).filter(
        models.ReviewDiscussionComment.CommentId == item_id,
        models.ReviewDiscussionComment.EntityStatus != "Archived"
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Review Comment not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    obj.UpdatedAt = datetime.utcnow()
    obj.UpdatedById = current_user.UserId

    db.commit()
    db.refresh(obj)
    crud.audit_log(db, 'ReviewDiscussionComment', getattr(obj, 'CommentId'), 'Update', changed_by=current_user.userName)
    return obj


@router.patch("/{item_id}/archive", summary="Archive Review Comment record.")
def archive_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only Admin and Project Manager can archive comments
    check_permission(current_user, [models.Role.ADMIN, models.Role.PROJECT_MANAGER])

    obj = db.query(models.ReviewDiscussionComment).filter(
        models.ReviewDiscussionComment.CommentId == item_id,
        models.ReviewDiscussionComment.EntityStatus != "Archived"
    ).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Review Comment not found")

    obj.EntityStatus = "Archived"
    obj.UpdatedAt = datetime.utcnow()
    obj.UpdatedById = current_user.UserId

    db.commit()

    crud.audit_log(db, 'ReviewDiscussionComment', getattr(obj, 'CommentId'), 'Archive', changed_by=current_user.userName)
    return {"status": "archived", "comment_id": obj.CommentId}
