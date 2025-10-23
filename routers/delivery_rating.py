from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from typing import Optional,List
import re
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from main.database import get_db
from main import models, schemas, crud

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

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
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),  
) -> models.User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")

    username = decode_token_and_get_username(access_token)
    user = db.query(models.User).filter(models.User.userName == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def generate_custom_rating_id(db: Session) -> str:
    prefix = "DEL-RAT-"
    last_rating = db.query(models.DeliveryRating).order_by(models.DeliveryRating.RatingId.desc()).first()

    if not last_rating or not re.match(rf"{prefix}\d{{3}}", last_rating.RatingId or ""):
        return f"{prefix}001"

    last_number = int(last_rating.RatingId.split("-")[-1])
    new_number = last_number + 1
    return f"{prefix}{new_number:03d}"

def is_pm_or_admin(user: models.User) -> bool:
    # Replace these strings with your enum if available
    return user.role_name in [models.Role.PROJECT_MANAGER, models.Role.ADMIN]

@router.post("/", response_model=schemas.DeliveryRatingOut, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating: schemas.DeliveryRatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if not is_pm_or_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Admin or Project Manager can create ratings.")

    existing_rating = db.query(models.DeliveryRating).filter(
        models.DeliveryRating.DeliverableId == rating.DeliverableId,
        models.DeliveryRating.AttributeId == rating.AttributeId,
        models.DeliveryRating.RatedForId == rating.RatedForId,
        models.DeliveryRating.RatedById == current_user.UserId,
    ).first()

    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating for this deliverable, attribute, and user combination already exists."
        )

    new_rating_id = generate_custom_rating_id(db)

    new_rating = models.DeliveryRating(
        RatingId=new_rating_id,
        RatedById=current_user.UserId,
        **rating.dict(exclude={"RatedById"})
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    crud.audit_log(db, "DeliveryRating", new_rating.RatingId, "Create", changed_by=current_user.userName)
    return new_rating

@router.get("/{rating_id}", response_model=schemas.DeliveryRatingOut)
def get_rating(
    rating_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if not is_pm_or_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Admin or Project Manager can view ratings.")

    rating = db.query(models.DeliveryRating).filter(models.DeliveryRating.RatingId == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    return rating

@router.patch("/{rating_id}", response_model=schemas.DeliveryRatingOut)
def update_rating(
    rating_id: str,
    rating_update: schemas.DeliveryRatingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if not is_pm_or_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Admin or Project Manager can update ratings.")

    rating = db.query(models.DeliveryRating).filter(models.DeliveryRating.RatingId == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    update_data = rating_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rating, key, value)
    db.commit()
    db.refresh(rating)

    crud.audit_log(db, "DeliveryRating", rating.RatingId, "Update", changed_by=current_user.userName)
    return rating
