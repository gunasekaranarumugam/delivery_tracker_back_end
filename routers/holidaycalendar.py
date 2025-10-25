<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie, Request
=======
from fastapi import APIRouter, Depends, HTTPException, Query, Cookie
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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
<<<<<<< HEAD


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

=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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
<<<<<<< HEAD
    existing = db.query(models.HolidayCalendar).filter_by(HolidayCalendarId=payload.HolidayCalendarId).first()
    if existing:
        raise HTTPException(status_code=400, detail="HolidayId already exists")

    #Check if holiday on this date already exists
=======
    existing = db.query(models.HolidayCalendar).filter_by(HolidayId=payload.HolidayId).first()
    if existing:
        raise HTTPException(status_code=400, detail="HolidayId already exists")

    # Check if holiday on this date already exists
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    existing_date = db.query(models.HolidayCalendar).filter_by(HolidayDate=payload.HolidayDate).first()
    if existing_date:
        raise HTTPException(status_code=400, detail="A holiday already exists on this date")

    obj = models.HolidayCalendar(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
<<<<<<< HEAD
    print(current_user)
    # Correct: pass actual UserId
    crud.audit_log(db, 'HolidayCalendar', obj.HolidayCalendarId, 'Create', changed_by=current_user.UserId)
=======

    crud.audit_log(db, 'HolidayCalendar', obj.HolidayId, 'Create', changed_by=current_user.userName)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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

<<<<<<< HEAD
@router.get("/{id}", response_model=schemas.HolidayCalendarRead, summary="Get Holiday by ID.")
def get_item(
    id: str,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme), 
):
    obj = db.query(models.HolidayCalendar).get(id)
=======
@router.get("/{item_id}", response_model=schemas.HolidayCalendarRead, summary="Get Holiday by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme), 
):
    obj = db.query(models.HolidayCalendar).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not obj:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return obj

<<<<<<< HEAD
@router.put("/{id}", response_model=schemas.HolidayCalendarRead, summary="Update Holiday record.")
def update_item(
    id: str,
=======
@router.put("/{item_id}", response_model=schemas.HolidayCalendarRead, summary="Update Holiday record.")
def update_item(
    item_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    payload: schemas.HolidayCalendarCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN", "BU-HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to update holiday calendar")

<<<<<<< HEAD
    obj = db.query(models.HolidayCalendar).get(id)
=======
    obj = db.query(models.HolidayCalendar).get(item_id)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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

<<<<<<< HEAD
    crud.audit_log(db, 'HolidayCalendar', obj.HolidayId, 'Update', changed_by=current_user.UserId)
    return obj


# Assuming this is part of your Holiday Calendar Router
@router.patch("/{id}", response_model=schemas.HolidayCalendarRead, summary="Partially update a Holiday Calendar.")
def update_holiday_calendar_partial(
    id: str,
    payload: schemas.HolidayCalendarUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    # 1. Permission Check
    # Only ADMIN or the BU HEAD who owns the calendar can modify it.
    if role_name not in ["ADMIN", "BU HEAD", "HR MANAGER"]: # Adjust "HR MANAGER" as needed
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify Holiday Calendars.")

    # 2. Fetch the Holiday Calendar record
    obj = db.query(models.HolidayCalendar).filter(
        models.HolidayCalendar.HolidayCalendarId == id,
        models.HolidayCalendar.EntityStatus != "Archived"
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday Calendar not found or archived")

    # 3. Ownership Check (if modifying BU Head/HR/BU Head)
    if role_name == "BU HEAD" and obj.BUId != user_bu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify calendars belonging to your Business Unit.")

    # 4. Perform Update
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        # Check if the update is to archive the calendar
        if key == "EntityStatus" and value == "Archived":
            # Explicitly disallow using PATCH for archiving if you want a dedicated /archive endpoint
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Use the dedicated PATCH /{id}/archive endpoint to archive this record.")

        setattr(obj, key, value)
        
    obj.UpdatedAt = now() 
    db.commit()
    db.refresh(obj)

    # 5. Audit Log
    crud.audit_log(
        db, 
        'HolidayCalendar', 
        obj.HolidayCalendarId, 
        'Update (Partial)', 
        changed_by=current_user.UserId
    )
    
    return obj
=======
    crud.audit_log(db, 'HolidayCalendar', obj.HolidayId, 'Update', changed_by=current_user.userName)
    return obj
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
