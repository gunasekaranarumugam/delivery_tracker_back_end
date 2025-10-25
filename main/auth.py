from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from main import models
from main.database import get_db
from jose import jwt
from datetime import datetime

SECRET_KEY = "super-secret-key"  # Load from env in production!
ALGORITHM = "HS256"

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

def get_current_user_from_cookie(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db),
) -> models.User:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    username = verify_jwt_token(access_token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.userName == username)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user