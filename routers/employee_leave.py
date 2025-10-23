from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from main.database import get_db
from main.models import EmployeeLeave, User, Employee, Role
from main.schemas import EmployeeLeaveCreate, EmployeeLeaveOut, EmployeeLeaveUpdate
from .deliverable import get_current_user_from_cookie

router = APIRouter()

ALLOWED_ROLES_CREATE_UPDATE = [Role.ADMIN, Role.BU_HEAD]
ALLOWED_ROLES_VIEW_ALL = [Role.ADMIN, Role.BU_HEAD]

def verify_bu_access(user: User, employee_bu_id: str):
    if user.role_name != Role.ADMIN and employee_bu_id != user.BUId:
        raise HTTPException(status_code=403, detail="Not authorized for this Business Unit")

@router.post("/", response_model=EmployeeLeaveOut, status_code=status.HTTP_201_CREATED)
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

@router.get("/{leave_id}", response_model=EmployeeLeaveOut)
def get_employee_leave(
    leave_id: str,
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

@router.patch("/{leave_id}", response_model=EmployeeLeaveOut)
def update_employee_leave(
    leave_id: str,
    data: EmployeeLeaveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ALLOWED_ROLES_CREATE_UPDATE:
        raise HTTPException(status_code=403, detail="Not authorized to update employee leaves")

    leave = db.query(EmployeeLeave).filter(EmployeeLeave.LeaveId == leave_id).first()
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

@router.get("/", response_model=List[EmployeeLeaveOut], summary="List leaves")
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
