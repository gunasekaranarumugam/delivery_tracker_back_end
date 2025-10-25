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

def now():
    return datetime.utcnow()
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



# ======================================================================
#                             EMPLOYEE SKILL ENDPOINTS
# ======================================================================

# ✅ POST - Create Employee Skill
@router.post("/", response_model=schemas.EmployeeSkillRead, status_code=status.HTTP_201_CREATED, summary="Assign a new skill to an employee")
def create_employee_skill(
    payload: schemas.EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)

    # Permission Check: ADMIN or BU HEAD can assign skills to others. Employees can assign/update their own skills.
    if role_name not in ["ADMIN", "BU HEAD"] and payload.EmployeeId != current_employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to assign skills to this employee")

    # Check for duplicate skill assignment
    exists = db.query(models.EmployeeSkill).filter(
        models.EmployeeSkill.EmployeeId == payload.EmployeeId,
        models.EmployeeSkill.SkillId == payload.SkillId,
        models.EmployeeSkill.EntityStatus != "Archived"
    ).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This skill is already assigned and active for this employee.")

    db_employee_skill = models.EmployeeSkill(
        EmployeeSkillId=str(uuid.uuid4()),
        **payload.dict(),
        CreatedAt=now(),
        UpdatedAt=now(),
        EntityStatus="Active"
    )
    db.add(db_employee_skill)
    db.commit()
    db.refresh(db_employee_skill)

    crud.audit_log(db, "EmployeeSkill", db_employee_skill.EmployeeSkillId, "Create", changed_by=current_user.UserId)
    return db_employee_skill


# ✅ GET - List All Employee Skills (with filtering)
@router.get("/", response_model=List[schemas.EmployeeSkillRead], summary="List all active employee skills (optional filter by employeeId)")
def list_employee_skills(
    employee_id: Optional[str] = Query(None, description="Filter skills by specific EmployeeId"),
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    query = db.query(models.EmployeeSkill).filter(models.EmployeeSkill.EntityStatus != "Archived")
    
    # Restrict viewing to self if not ADMIN/BU HEAD
    if role_name not in ["ADMIN", "BU HEAD"]:
        if current_employee_id:
            query = query.filter(models.EmployeeSkill.EmployeeId == current_employee_id)
        else:
            # Should not happen if user is authenticated, but provides safe default
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view skills data.")
            
    # Apply explicit filter if provided AND user is authorized to view others' data
    elif employee_id:
        query = query.filter(models.EmployeeSkill.EmployeeId == employee_id)
        
    return query.offset(offset).limit(limit).all()


# ✅ GET - Employee Skill by ID
@router.get("/{id}", response_model=schemas.EmployeeSkillRead, summary="Get a specific employee skill record by ID")
def get_employee_skill(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    obj = db.query(models.EmployeeSkill).filter(
        models.EmployeeSkill.EmployeeSkillId == id,
        models.EmployeeSkill.EntityStatus != "Archived"
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee skill record not found or archived")

    # Access Check: Must be ADMIN/BU HEAD or the employee themselves
    if role_name not in ["ADMIN", "BU HEAD"] and obj.EmployeeId != current_employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this record")
        
    return obj


# ✅ PUT - Full Update (Replace entire resource)
@router.put("/{id}", response_model=schemas.EmployeeSkillRead, summary="Fully update an employee skill record")
def update_employee_skill_full(
    id: str,
    payload: schemas.EmployeeSkillCreate, # Using Create schema for full replacement
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)

    obj = db.query(models.EmployeeSkill).filter(models.EmployeeSkill.EmployeeSkillId == id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee skill record not found")

    # Permission Check: Must be ADMIN/BU HEAD or the employee themselves
    if role_name not in ["ADMIN", "BU HEAD"] and obj.EmployeeId != current_employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this record")

    # Perform update (Replace all fields using payload data)
    for key, value in payload.dict().items():
        setattr(obj, key, value)
        
    obj.UpdatedAt = now()
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "EmployeeSkill", obj.EmployeeSkillId, "Update(PUT)", changed_by=current_user.UserId)
    return obj


# ✅ PATCH - Partial Update
@router.patch("/{id}", response_model=schemas.EmployeeSkillRead, summary="Partially update an employee skill record")
def update_employee_skill_partial(
    id: str,
    payload: schemas.EmployeeSkillUpdate, # Using Update schema for partial changes
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)

    obj = db.query(models.EmployeeSkill).filter(models.EmployeeSkill.EmployeeSkillId == id).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee skill record not found")

    # Permission Check: Must be ADMIN/BU HEAD or the employee themselves
    if role_name not in ["ADMIN", "BU HEAD"] and obj.EmployeeId != current_employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this record")

    # Perform partial update
    update_data = payload.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    obj.UpdatedAt = now()
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "EmployeeSkill", obj.EmployeeSkillId, "Update(PATCH)", changed_by=current_user.UserId)
    return obj


