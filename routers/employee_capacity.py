from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from main.database import get_db
from main.models import EmployeeCapacity, User, Role  # Assuming Role is an enum or constants
from main.schemas import EmployeeCapacityCreate, EmployeeCapacityOut, EmployeeCapacityUpdate
from .deliverable import get_current_user_from_cookie

router = APIRouter()

ALLOWED_ROLES = [Role.ADMIN, Role.BU_HEAD]

def verify_bu_access(user: User, bu_id: str):
    if user.role_name != Role.ADMIN and user.BUId != bu_id:
        raise HTTPException(status_code=403, detail="Operation not permitted outside your Business Unit")

@router.post("/", response_model=EmployeeCapacityOut, status_code=status.HTTP_201_CREATED)
def create_employee_capacity(
    data: EmployeeCapacityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Not authorized to create employee capacity")

    verify_bu_access(current_user, data.BUId)

    existing_capacity = db.query(EmployeeCapacity).filter(
        EmployeeCapacity.EmployeeId == data.EmployeeId,
        EmployeeCapacity.BUId == data.BUId
    ).first()

    if existing_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee capacity for this BU already exists."
        )

    new_capacity = EmployeeCapacity(
        EmployeeCapacityId=str(uuid.uuid4()),
        **data.dict()
    )
    db.add(new_capacity)
    db.commit()
    db.refresh(new_capacity)
    return new_capacity

@router.get("/{employee_capacity_id}", response_model=EmployeeCapacityOut)
def get_employee_capacity(
    employee_capacity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    capacity = db.query(EmployeeCapacity).filter(EmployeeCapacity.EmployeeCapacityId == employee_capacity_id).first()
    if not capacity:
        raise HTTPException(status_code=404, detail="Employee Capacity not found")

    verify_bu_access(current_user, capacity.BUId)

    return capacity

@router.patch("/{employee_capacity_id}", response_model=EmployeeCapacityOut)
def update_employee_capacity(
    employee_capacity_id: str,
    data: EmployeeCapacityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Not authorized to update employee capacity")

    capacity = db.query(EmployeeCapacity).filter(EmployeeCapacity.EmployeeCapacityId == employee_capacity_id).first()
    if not capacity:
        raise HTTPException(status_code=404, detail="Employee Capacity not found")

    verify_bu_access(current_user, capacity.BUId)

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(capacity, key, value)

    db.commit()
    db.refresh(capacity)
    return capacity

@router.get("/", response_model=List[EmployeeCapacityOut], summary="List employee capacities")
def list_employee_capacities(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    query = db.query(EmployeeCapacity)
    if current_user.role_name != Role.ADMIN:
        query = query.filter(EmployeeCapacity.BUId == current_user.BUId)

    capacities = query.offset(offset).limit(limit).all()
    return capacities
