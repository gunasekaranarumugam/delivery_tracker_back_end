from fastapi import APIRouter, Depends, HTTPException, Query, status, Cookie, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import List, Optional
from datetime import datetime
import uuid
from fastapi.security import OAuth2PasswordBearer
# Assuming these are available in your main directory structure
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

# ----------------------------------------------------------------------
#                             HOLIDAY ENDPOINTS
# ----------------------------------------------------------------------

# ✅ POST - Create Holiday
@router.post("/", response_model=schemas.HolidayRead, status_code=status.HTTP_201_CREATED, summary="Create a new Holiday entry")
def create_holiday(
    payload: schemas.HolidayCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)

    # Permission check: Only ADMIN or roles managing holidays should create
    if role_name not in ["ADMIN", "HR MANAGER"]: # Adjust "HR MANAGER" as per your roles
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only ADMIN or HR MANAGER can create holidays")

    # Check for existing holiday on the same date for the same calendar
    exists = db.query(models.Holiday).filter(
        models.Holiday.Date == payload.Date,
        models.Holiday.HolidayCalendarId == payload.HolidayCalendarId
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"A holiday already exists on {payload.Date} for calendar {payload.HolidayCalendarId}"
        )

    db_holiday = models.Holiday(
        HolidayId=str(uuid.uuid4()),
        **payload.dict(),
        CreatedAt=now(),
        UpdatedAt=now()
    )
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)

    crud.audit_log(
        db,
        entity_type="Holiday",
        entity_id=db_holiday.HolidayId,
        action="Create",
        action_performed_by=current_user.UserId,
        previous_value="N/A"
    )
    return db_holiday


# ✅ GET - List Holidays
@router.get("/", response_model=List[schemas.HolidayRead], summary="List Holidays")
def list_holidays(
    calendar_id: Optional[str] = Query(None, description="Filter by Holiday Calendar ID"),
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Public read access is usually fine for holidays
    query = db.query(models.Holiday)
    
    if calendar_id:
        query = query.filter(models.Holiday.HolidayCalendarId == calendar_id)
        
    return query.offset(offset).limit(limit).all()


# ✅ GET - Holiday by ID
@router.get("/{id}", response_model=schemas.HolidayRead, summary="Get Holiday by ID")
def get_holiday(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.Holiday).filter(models.Holiday.HolidayId == id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found")

    # No specific permission check for reading a single public holiday is typically needed
    return obj


# ✅ PUT - Update Holiday
@router.put("/{id}", response_model=schemas.HolidayRead, summary="Update Holiday")
def update_holiday(
    id: str,
    payload: schemas.HolidayUpdate, # Use the Update schema here
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)

    if role_name not in ["ADMIN", "HR MANAGER"]: # Adjust role as needed
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only ADMIN or HR MANAGER can update holidays")

    obj = db.query(models.Holiday).filter(models.Holiday.HolidayId == id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found")

    # Update only the fields provided in the payload
    update_data = payload.dict(exclude_unset=True)

    # Check for potential conflict on date/calendar if both are updated
    if 'Date' in update_data or 'HolidayCalendarId' in update_data:
        new_date = update_data.get('Date', obj.Date)
        new_calendar_id = update_data.get('HolidayCalendarId', obj.HolidayCalendarId)
        
        conflict = db.query(models.Holiday).filter(
            models.Holiday.Date == new_date,
            models.Holiday.HolidayCalendarId == new_calendar_id,
            models.Holiday.HolidayId != id
        ).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An identical holiday entry already exists.")


    for key, value in update_data.items():
        setattr(obj, key, value)
        
    obj.UpdatedAt = now()
    db.commit()
    db.refresh(obj)

    crud.audit_log(
        db,
        entity_type="Holiday",
        entity_id=obj.HolidayId,
        action="Update",
        action_performed_by=current_user.UserId
    )
    return obj


@router.patch("/{id}/archive", summary="Archive Holiday record.")
def archive_holiday(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    
    # 1. Permission Check
    # Only ADMIN or the Holiday manager role can archive/modify holidays.
    # NOTE: Assuming "HR_MANAGER" or similar role is responsible for the calendar.
    if role_name not in ["ADMIN", "HR_MANAGER"]: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to archive holiday")

    # 2. Fetch the Holiday object
    # Using .filter().first() instead of .get() as it's more universal in SQLAlchemy
    obj = db.query(models.Holiday).filter(models.Holiday.HolidayId == id).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found")

    # 3. BU Head/Ownership Check (Not applicable for Holiday, but checking calendar ownership if needed)
    # Holidays are linked to HolidayCalendarId, not BUId directly. 
    # The current user's BU is irrelevant unless you check if they own the Holiday's Calendar.
    # I'll omit this complex check for now, assuming ADMIN/HR_MANAGER can archive any holiday.
    
    # If you needed to check Calendar ownership (e.g., BU Head owning a specific calendar):
    # if role_name == "BU_HEAD":
    #     calendar = db.query(models.HolidayCalendar).filter(models.HolidayCalendar.HolidayCalendarId == obj.HolidayCalendarId).first()
    #     if calendar.BUId != current_user.BUId:
    #         raise HTTPException(status_code=403, detail="Cannot archive holiday in a calendar outside your BU.")


    # 4. Perform Archive
    # NOTE: This assumes 'EntityStatus' exists on the models.Holiday SQLAlchemy model.
    if hasattr(obj, 'EntityStatus'):
        obj.EntityStatus = "Archived"
        if hasattr(obj, 'UpdatedAt'):
            obj.UpdatedAt = now()  # Use the 'now' function defined in your helper
        
        db.commit()

        # 5. Audit Log
        crud.audit_log(
            db, 
            'Holiday', 
            getattr(obj, 'HolidayId'), 
            'Archive', 
            changed_by=current_user.UserId # Use UserId for consistency
        )
        return {"status": "archived", "HolidayId": id}
    else:
        # Fallback if EntityStatus is not a column (better to use DELETE)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Holiday model does not support EntityStatus field for archiving. Use DELETE instead."
        )


