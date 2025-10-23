from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from typing import List,Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from main.auth import get_current_user_from_cookie  # adjust import as needed
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError
from jose import jwt
router = APIRouter()


SECRET_KEY = "super-secret-key"
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

@router.post("/", response_model=schemas.FeedbackCategoryMasterRead, summary="Add new Feedback Category record.")
def create_item(
    payload: schemas.FeedbackCategoryMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    if current_user.role_name not in ["ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to create feedback categories")

    existing = db.query(models.FeedbackCategoryMaster).filter_by(FeedbackCategoryId=payload.FeedbackCategoryId).first()
    if existing:
        raise HTTPException(status_code=400, detail="FeedbackCategoryId already exists")

    obj = models.FeedbackCategoryMaster(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'FeedbackCategoryMaster', obj.FeedbackCategoryId, 'Create', changed_by=current_user.userName)
    return obj

@router.get("/", response_model=List[schemas.FeedbackCategoryMasterRead], summary="Get list of Feedback Category records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name in ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']:
        raise HTTPException(status_code=403, detail="Not authorized to view feedback categories")

    q = db.query(models.FeedbackCategoryMaster)
    return q.offset(offset).limit(limit).all()

@router.get("/{item_id}", response_model=schemas.FeedbackCategoryMasterRead, summary="Get Feedback Category by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name in ['DEVELOPER', 'TEAM MEMBER', 'DELIVERY MANAGER']:
        raise HTTPException(status_code=403, detail="Not authorized to view feedback categories")

    obj = db.query(models.FeedbackCategoryMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback Category not found")
    return obj

@router.put("/{item_id}", response_model=schemas.FeedbackCategoryMasterRead, summary="Update Feedback Category record.")
def update_item(
    item_id: str,
    payload: schemas.FeedbackCategoryMasterCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to update feedback categories")

    obj = db.query(models.FeedbackCategoryMaster).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Feedback Category not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'FeedbackCategoryMaster', obj.FeedbackCategoryId, 'Update', changed_by=current_user.userName)
    return obj
