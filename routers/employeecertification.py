from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from main import models, schemas, crud
from main.database import get_db
from .deliverable import get_current_user_from_cookie  # your auth dependency

router = APIRouter()

@router.post("/", response_model=schemas.EmployeeCertificationRead, summary="Add new Employee Certification record.")
def create_item(
    payload: schemas.EmployeeCertificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    # Only ADMIN or BU_HEAD allowed to create
    if current_user.role_name not in ["ADMIN", "BU_HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to create employee certifications")

    employee = db.query(models.Employee).filter_by(EmployeeId=payload.EmployeeId).first()
    if not employee:
        raise HTTPException(status_code=400, detail="Invalid EmployeeId")

    # BU_HEAD can only create certifications for employees in their BU
    if current_user.role_name == "BU_HEAD" and employee.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot create certification for employee outside your BU")

    certification = db.query(models.CertificationMaster).filter_by(CertificationId=payload.CertificationId).first()
    if not certification:
        raise HTTPException(status_code=400, detail="Invalid CertificationId")

    existing = db.query(models.EmployeeCertification).filter_by(
        EmployeeId=payload.EmployeeId,
        CertificationId=payload.CertificationId
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee already has this certification")

    obj = models.EmployeeCertification(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'EmployeeCertification', obj.EmployeeCertificationId, 'Create', changed_by=current_user.userName)
    return obj

@router.get("/", response_model=List[schemas.EmployeeCertificationRead], summary="Get list of Employee Certification records.")
def list_items(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    q = db.query(models.EmployeeCertification).join(models.Employee)

    if current_user.role_name == "ADMIN":
        # Admin sees all certifications
        pass

    elif current_user.role_name == "PROJECT MANAGER":
        # PM sees certifications of employees involved in projects they manage
        q = q.join(models.Employee.assigned_tasks) \
             .join(models.Task.deliverable) \
             .join(models.Deliverable.project) \
             .filter(models.Project.DeliveryManagerId == current_user.UserId)

    else:
        # Others see only certifications of employees in their BU
        q = q.filter(models.Employee.BUId == current_user.BUId)

    return q.offset(offset).limit(limit).all()

@router.get("/{item_id}", response_model=schemas.EmployeeCertificationRead, summary="Get Employee Certification by ID.")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.EmployeeCertification).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Certification not found")

    if current_user.role_name != "ADMIN":
        employee = db.query(models.Employee).filter_by(EmployeeId=obj.EmployeeId).first()
        if not employee or employee.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Not authorized to view this certification")

    return obj

@router.put("/{item_id}", response_model=schemas.EmployeeCertificationRead, summary="Update Employee Certification record.")
def update_item(
    item_id: str,
    payload: schemas.EmployeeCertificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ["ADMIN", "BU_HEAD"]:
        raise HTTPException(status_code=403, detail="Not authorized to update employee certifications")

    obj = db.query(models.EmployeeCertification).get(item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Certification not found")

    employee = db.query(models.Employee).filter_by(EmployeeId=obj.EmployeeId).first()
    if current_user.role_name == "BU_HEAD" and employee.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update certification outside your BU")

    for k, v in payload.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, 'EmployeeCertification', obj.EmployeeCertificationId, 'Update', changed_by=current_user.userName)
    return obj
