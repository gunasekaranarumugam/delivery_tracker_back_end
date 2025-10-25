<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Query
=======
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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

<<<<<<< HEAD
@router.post("/", response_model=schemas.DeliveryRatingRead, status_code=status.HTTP_201_CREATED)
=======
@router.post("/", response_model=schemas.DeliveryRatingOut, status_code=status.HTTP_201_CREATED)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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

<<<<<<< HEAD
    crud.audit_log(db, "DeliveryRating", new_rating.RatingId, "Create", changed_by=current_user.UserId)
    return new_rating

@router.get("/{id}", response_model=schemas.DeliveryRatingRead)
def get_rating(
    id: str,
=======
    crud.audit_log(db, "DeliveryRating", new_rating.RatingId, "Create", changed_by=current_user.userName)
    return new_rating

@router.get("/{rating_id}", response_model=schemas.DeliveryRatingOut)
def get_rating(
    rating_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if not is_pm_or_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Admin or Project Manager can view ratings.")

<<<<<<< HEAD
    rating = db.query(models.DeliveryRating).filter(models.DeliveryRating.RatingId == id).first()
=======
    rating = db.query(models.DeliveryRating).filter(models.DeliveryRating.RatingId == rating_id).first()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    return rating

<<<<<<< HEAD
@router.patch("/{id}", response_model=schemas.DeliveryRatingRead)
def update_rating(
    id: str,
=======
@router.patch("/{rating_id}", response_model=schemas.DeliveryRatingOut)
def update_rating(
    rating_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    rating_update: schemas.DeliveryRatingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if not is_pm_or_admin(current_user):
        raise HTTPException(status_code=403, detail="Only Admin or Project Manager can update ratings.")

<<<<<<< HEAD
    rating = db.query(models.DeliveryRating).filter(models.DeliveryRating.RatingId == id).first()
=======
    rating = db.query(models.DeliveryRating).filter(models.DeliveryRating.RatingId == rating_id).first()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    update_data = rating_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rating, key, value)
    db.commit()
    db.refresh(rating)

<<<<<<< HEAD
    crud.audit_log(db, "DeliveryRating", rating.RatingId, "Update", changed_by=current_user.UserId)
    return rating


@router.get("/", response_model=List[schemas.DeliveryRatingRead], summary="List Delivery Rating records with optional filtering.")
def list_delivery_ratings(
    rated_employee_id: Optional[str] = Query(None, description="Filter by Employee ID who was rated"),
    rating_given_by_id: Optional[str] = Query(None, description="Filter by Employee ID who gave the rating"),
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    query = db.query(models.DeliveryRating).filter(models.DeliveryRating.EntityStatus != "Archived")

    # 1. Permission Check and Scoping
    if role_name not in ["ADMIN", "BU HEAD", "HR MANAGER"]:
        # Non-administrative users can only view ratings relevant to them
        if current_employee_id:
            query = query.filter(
                (models.DeliveryRating.RatedEmployeeId == current_employee_id) |
                (models.DeliveryRating.RatingGivenById == current_employee_id)
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="You do not have permission to view global rating data.")

    # 2. Apply Filters (even high-level users can filter)
    if rated_employee_id:
        query = query.filter(models.DeliveryRating.RatedEmployeeId == rated_employee_id)
        
    if rating_given_by_id:
        query = query.filter(models.DeliveryRating.RatingGivenById == rating_given_by_id)
        
    return query.offset(offset).limit(limit).all()

@router.put("/{id}", response_model=schemas.DeliveryRatingRead, summary="Fully update (replace) a Delivery Rating record.")
def update_delivery_rating_full(
    id: str,
    payload: schemas.DeliveryRatingCreate, # Assuming Create schema holds all required fields
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    # 1. Fetch the record
    obj = db.query(models.DeliveryRating).filter(
        models.DeliveryRating.DeliveryRatingId == id, 
        models.DeliveryRating.EntityStatus != "Archived" 
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery Rating record not found or archived")

    # 2. Permission Check
    is_admin = role_name == "ADMIN"
    is_rater = obj.RatingGivenById == current_employee_id
    
    if not (is_admin or is_rater):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to modify this rating. Only the rater or ADMIN can update.")

    # 3. Perform Full Update
    update_data = payload.dict() 
    
    for key, value in update_data.items():
        if key == "DeliveryRatingId":
             continue # Don't overwrite ID
        setattr(obj, key, value)
        
    # Set audit fields
    if hasattr(obj, 'UpdatedAt'):
        obj.UpdatedAt = now() 
    if hasattr(obj, 'UpdatedById'):
        obj.UpdatedById = current_user.UserId

    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    crud.audit_log(
        db, 
        'DeliveryRating', 
        obj.DeliveryRatingId, 
        'Update (PUT)', 
        changed_by=current_user.UserId 
    )
    
    return obj
=======
    crud.audit_log(db, "DeliveryRating", rating.RatingId, "Update", changed_by=current_user.userName)
    return rating
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
