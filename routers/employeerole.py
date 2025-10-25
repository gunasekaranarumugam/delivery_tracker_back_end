from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from main.auth import get_current_user_from_cookie  # adjust import as per your project structure
from fastapi.security import OAuth2PasswordBearer
router = APIRouter()
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

@router.post("/", response_model=schemas.EmployeeRoleRead, summary="Add new Employee Role record.")
def create_item(
    payload: schemas.EmployeeRoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN", "BU_HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to create employee roles")

    employee = db.query(models.Employee).filter_by(EmployeeId=payload.EmployeeId).first()
    if not employee:
        raise HTTPException(status_code=400, detail="Invalid EmployeeId")

    # Optional: Restrict BU_HEAD to only their BU employees
    if current_user.role_name == "BU_HEAD" and employee.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot assign roles to employees outside your BU")

    role = db.query(models.RoleMaster).filter_by(RoleId=payload.RoleId).first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid RoleId")

    existing = db.query(models.EmployeeRole).filter_by(EmployeeId=payload.EmployeeId, RoleId=payload.RoleId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee already has this role")

    obj = models.EmployeeRole(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'EmployeeRole', getattr(obj, 'EmployeeRoleId'), 'Create',changed_by=current_user.UserId)
    return obj


@router.get("/", response_model=List[schemas.EmployeeRoleRead], summary="Get list of Employee Role records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    q = db.query(models.EmployeeRole)

    # Optional: restrict BU_HEAD to only their BU's employees
    if current_user.role_name == "BU_HEAD":
        q = q.join(models.Employee).filter(models.Employee.BUId == current_user.BUId)

    return q.offset(offset).limit(limit).all()


@router.get("/{id}", response_model=schemas.EmployeeRoleRead, summary="Get Employee Role by ID.")
def get_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.EmployeeRole).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Role not found")

    if current_user.role_name == "BU_HEAD":
        employee = db.query(models.Employee).filter_by(EmployeeId=obj.EmployeeId).first()
        if employee.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Not authorized to view this role")

    return obj


@router.put("/{id}", response_model=schemas.EmployeeRoleRead, summary="Update Employee Role record.")
def update_item(
    id: str,
    payload: schemas.EmployeeRoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN", "BU_HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to update employee roles")

    obj = db.query(models.EmployeeRole).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Role not found")

    employee = db.query(models.Employee).filter_by(EmployeeId=obj.EmployeeId).first()
    if current_user.role_name == "BU_HEAD" and employee.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update roles of employees outside your BU")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'EmployeeRole', getattr(obj, 'EmployeeRoleId'), 'Update', changed_by=current_user.UserId)
    return obj


@router.patch("/{id}", response_model=schemas.EmployeeRead, summary="Partially update an Employee record.")
def update_employee_partial(
    id: str,
    payload: schemas.EmployeeUpdate, # Assuming this schema has Optional fields like RoleId, Name, etc.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Retrieve user's role and associated employee information (reusing helper from previous context)
    role_name, user_bu_id = get_user_role_and_bu(db, current_user)
    
    # 1. Fetch the Employee record to be updated
    obj = db.query(models.Employee).filter(models.Employee.EmployeeId == id).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    # 2. Permission and Ownership Check

    # Check 2a: Only ADMIN/BU HEAD can modify other employees.
    # Employees should only be able to update non-sensitive info (like address/phone) on themselves.
    # For simplicity here, we'll restrict to ADMIN/BU HEAD or the employee updating themselves.
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    is_admin_or_bu_head = role_name in ["ADMIN", "BU HEAD"]
    is_self_update = obj.EmployeeId == current_employee_id
    
    if not (is_admin_or_bu_head or is_self_update):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this employee.")

    # Check 2b: BU HEAD can only modify employees in their own BU.
    if role_name == "BU HEAD" and obj.BUId != user_bu_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update employee outside your Business Unit")

    # Check 2c: Prevent non-ADMIN/BU HEAD from changing sensitive fields (like RoleId, BUId)
    update_data = payload.model_dump(exclude_unset=True)
    
    sensitive_fields = ["RoleId", "BUId", "Designation"]
    
    if not is_admin_or_bu_head:
        for field in sensitive_fields:
            if field in update_data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied: Cannot update '{field}'")
                
    # 3. Perform Update
    
    for key, value in update_data.items():
        setattr(obj, key, value)
        
    obj.UpdatedAt = now() # Assuming 'now()' helper is available
    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    crud.audit_log(
        db, 
        'Employee', 
        obj.EmployeeId, 
        'Update (Partial)', 
        changed_by=current_user.UserId # Use UserId for consistency
    )
    
    return obj

