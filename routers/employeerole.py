"""from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from main.auth import get_current_user_from_cookie  # adjust import as per your project structure

router = APIRouter()

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

    crud.audit_log(db, 'EmployeeRole', getattr(obj, 'EmployeeRoleId'), 'Create')
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


@router.get("/{item_id}", response_model=schemas.EmployeeRoleRead, summary="Get Employee Role by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.EmployeeRole).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Role not found")

    if current_user.role_name == "BU_HEAD":
        employee = db.query(models.Employee).filter_by(EmployeeId=obj.EmployeeId).first()
        if employee.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Not authorized to view this role")

    return obj


@router.put("/{item_id}", response_model=schemas.EmployeeRoleRead, summary="Update Employee Role record.")
def update_item(
    item_id: str,
    payload: schemas.EmployeeRoleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN", "BU_HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to update employee roles")

    obj = db.query(models.EmployeeRole).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Role not found")

    employee = db.query(models.Employee).filter_by(EmployeeId=obj.EmployeeId).first()
    if current_user.role_name == "BU_HEAD" and employee.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update roles of employees outside your BU")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'EmployeeRole', getattr(obj, 'EmployeeRoleId'), 'Update', changed_by=current_user.userName)
    return obj
"""
