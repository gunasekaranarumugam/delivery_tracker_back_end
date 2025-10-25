from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List
from main import models, schemas, crud
from main.database import get_db
from main.models import EmployeeLeave, User, Employee, Role
from main.schemas import EmployeeLeaveCreate, EmployeeLeaveRead, EmployeeLeaveUpdate
from .deliverable import get_current_user_from_cookie

router = APIRouter()

ALLOWED_ROLES_CREATE_UPDATE = [Role.ADMIN, Role.BU_HEAD]
ALLOWED_ROLES_VIEW_ALL = [Role.ADMIN, Role.BU_HEAD]

def verify_bu_access(user: User, employee_bu_id: str):
    if user.role_name != Role.ADMIN and employee_bu_id != user.BUId:
        raise HTTPException(status_code=403, detail="Not authorized for this Business Unit")

@router.post("/", response_model=EmployeeLeaveCreate, status_code=status.HTTP_201_CREATED)
def create_employee_leave(
    data: EmployeeLeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ALLOWED_ROLES_CREATE_UPDATE:
        raise HTTPException(status_code=403, detail="Not authorized to create employee leaves")

    employee = db.query(Employee).filter(Employee.EmployeeId == data.EmployeeId).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    verify_bu_access(current_user, employee.BUId)

    existing_leave = db.query(EmployeeLeave).filter(
        EmployeeLeave.EmployeeId == data.EmployeeId,
        EmployeeLeave.LeaveDate == data.LeaveDate
    ).first()
    if existing_leave:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave for this employee on this date already exists."
        )

    new_leave = EmployeeLeave(
        LeaveId=str(uuid.uuid4()),
        **data.dict()
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave

@router.get("/{id}", response_model=EmployeeLeaveRead)
def get_employee_leave(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    leave = db.query(EmployeeLeave).filter(EmployeeLeave.LeaveId == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Employee Leave not found")

    employee = db.query(Employee).filter(Employee.EmployeeId == leave.EmployeeId).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if current_user.role_name == Role.ADMIN:
        return leave

    if current_user.role_name in ALLOWED_ROLES_VIEW_ALL:
        verify_bu_access(current_user, employee.BUId)
        return leave

    # Otherwise only the employee can view their own leave
    if leave.EmployeeId != current_user.UserId:
        raise HTTPException(status_code=403, detail="Not authorized to view this leave")

    return leave

@router.patch("/{id}", response_model=EmployeeLeaveUpdate)
def update_employee_leave(
    id: str,
    data: EmployeeLeaveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ALLOWED_ROLES_CREATE_UPDATE:
        raise HTTPException(status_code=403, detail="Not authorized to update employee leaves")

    leave = db.query(EmployeeLeave).filter(EmployeeLeave.LeaveId == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Employee Leave not found")

    employee = db.query(Employee).filter(Employee.EmployeeId == leave.EmployeeId).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    verify_bu_access(current_user, employee.BUId)

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(leave, key, value)

    db.commit()
    db.refresh(leave)
    return leave

@router.get("/", response_model=List[EmployeeLeaveRead], summary="List leaves")
def list_employee_leaves(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    query = db.query(EmployeeLeave)

    if current_user.role_name == Role.ADMIN:
        pass  # Admin can see all leaves
    elif current_user.role_name in ALLOWED_ROLES_VIEW_ALL:
        query = query.join(Employee).filter(Employee.BUId == current_user.BUId)
    else:
        query = query.filter(EmployeeLeave.EmployeeId == current_user.UserId)

    leaves = query.offset(offset).limit(limit).all()
    return leaves

@router.put("/{id}", response_model=schemas.EmployeeLeaveRead, summary="Fully update (replace) an Employee Leave request.")
def update_employee_leave_full(
    id: str,
    payload: schemas.EmployeeLeaveCreate, # Requires ALL fields for a full replacement
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    current_employee_id = get_employee_id_by_user_id(db, current_user.UserId)
    
    # 1. Permission Check
    
    # Fetch the record first to check ownership
    obj = db.query(models.EmployeeLeave).filter(
        models.EmployeeLeave.EmployeeLeaveId == id, 
        models.EmployeeLeave.EntityStatus != "Archived" 
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee Leave record not found or archived")

    # Only the submitting employee or ADMIN/HR can update the request
    is_owner = obj.EmployeeId == current_employee_id
    is_admin_or_hr = role_name in ["ADMIN", "HR MANAGER"]

    if not (is_owner or is_admin_or_hr):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to modify this leave request.")

    # Prevent modification if the request is already approved or rejected
    if obj.Status in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Cannot update a leave request with status: {obj.Status}")

    # 2. Perform Full Update (Replace all fields using payload data)
    update_data = payload.dict() 
    
    for key, value in update_data.items():
        # Prevent client from changing the ID
        if key == "EmployeeLeaveId":
             continue
        setattr(obj, key, value)
        
    # Reset Status to PENDING if it was previously PENDING or DRAFT, 
    # as any modification requires re-approval.
    obj.Status = "PENDING"
    
    # Set audit fields
    if hasattr(obj, 'UpdatedAt'):
        obj.UpdatedAt = now() 
    if hasattr(obj, 'UpdatedById'):
        obj.UpdatedById = current_user.UserId

    db.commit()
    db.refresh(obj)

    # 3. Audit Log
    crud.audit_log(
        db, 
        'EmployeeLeave', 
        obj.EmployeeLeaveId, 
        'Update (PUT)', 
        changed_by=current_user.UserId 
    )
    
    return obj
