from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
from typing import List,Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from main.auth import get_current_user_from_cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt

router = APIRouter()
from sqlalchemy.orm import joinedload
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
# Auth: Get current user from JWT token in cookie
def get_current_user_from_cookie(
    access_token: str = Cookie(None),
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> models.User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.userName == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found, please login.")
    return user

@router.post("/", response_model=schemas.HolidayCalendarRead, summary="Add new Holiday record.")
def create_item(
    payload: schemas.HolidayCalendarCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie)
):
    if current_user.role_name not in ["ADMIN", "BU-HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to manage holiday calendar")

    # Check if HolidayId already exists
    existing = db.query(models.HolidayCalendar).filter_by(HolidayId=payload.HolidayId).first()
    if existing:
        raise HTTPException(status_code=400, detail="HolidayId already exists")

    # Check if holiday on this date already exists
    existing_date = db.query(models.HolidayCalendar).filter_by(HolidayDate=payload.HolidayDate).first()
    if existing_date:
        raise HTTPException(status_code=400, detail="A holiday already exists on this date")

    obj = models.HolidayCalendar(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'HolidayCalendar', obj.HolidayId, 'Create', changed_by=current_user.userName)
    return obj

@router.get("/", response_model=List[schemas.HolidayCalendarRead], summary="Get list of Holiday records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme), 
):
    q = db.query(models.HolidayCalendar)
    return q.offset(offset).limit(limit).all()

@router.get("/{item_id}", response_model=schemas.HolidayCalendarRead, summary="Get Holiday by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme), 
):
    obj = db.query(models.HolidayCalendar).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return obj

@router.put("/{item_id}", response_model=schemas.HolidayCalendarRead, summary="Update Holiday record.")
def update_item(
    item_id: str,
    payload: schemas.HolidayCalendarCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN", "BU-HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to update holiday calendar")

    obj = db.query(models.HolidayCalendar).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Holiday not found")

    # Optional: check if updating to a date that conflicts with another holiday
    if payload.HolidayDate != obj.HolidayDate:
        conflict = db.query(models.HolidayCalendar).filter(
            models.HolidayCalendar.HolidayDate == payload.HolidayDate,
            models.HolidayCalendar.HolidayId != item_id
        ).first()
        if conflict:
            raise HTTPException(status_code=400, detail="A holiday already exists on this date")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'HolidayCalendar', obj.HolidayId, 'Update', changed_by=current_user.userName)
    return obj
