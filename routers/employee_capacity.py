from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import uuid
<<<<<<< HEAD
from main import models, schemas, crud
=======

>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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

<<<<<<< HEAD
@router.get("/{id}", response_model=EmployeeCapacityOut)
def get_employee_capacity(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    capacity = db.query(EmployeeCapacity).filter(EmployeeCapacity.EmployeeCapacityId == id).first()
=======
@router.get("/{employee_capacity_id}", response_model=EmployeeCapacityOut)
def get_employee_capacity(
    employee_capacity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    capacity = db.query(EmployeeCapacity).filter(EmployeeCapacity.EmployeeCapacityId == employee_capacity_id).first()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    if not capacity:
        raise HTTPException(status_code=404, detail="Employee Capacity not found")

    verify_bu_access(current_user, capacity.BUId)

    return capacity

<<<<<<< HEAD
@router.patch("/{id}", response_model=EmployeeCapacityOut)
def update_employee_capacity(
    id: str,
=======
@router.patch("/{employee_capacity_id}", response_model=EmployeeCapacityOut)
def update_employee_capacity(
    employee_capacity_id: str,
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    data: EmployeeCapacityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Not authorized to update employee capacity")

<<<<<<< HEAD
    capacity = db.query(EmployeeCapacity).filter(EmployeeCapacity.EmployeeCapacityId == id).first()
=======
    capacity = db.query(EmployeeCapacity).filter(EmployeeCapacity.EmployeeCapacityId == employee_capacity_id).first()
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
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
<<<<<<< HEAD

@router.put("/{id}", response_model=schemas.EmployeeCapacityRead, summary="Fully update (replace) an Employee Capacity record.")
def update_employee_capacity_full(
    id: str,
    payload: schemas.EmployeeCapacityCreate, # Requires ALL fields for a full replacement
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    role_name = get_user_role(db, current_user)
    
    # 1. Permission Check
    # Restrict modification to ADMIN, BU HEAD, or HR MANAGER.
    if role_name not in ["ADMIN", "BU HEAD", "HR MANAGER"]: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to modify Employee Capacity records.")

    # 2. Fetch the EmployeeCapacity record
    # Assuming the primary key is EmployeeCapacityId
    obj = db.query(models.EmployeeCapacity).filter(
        models.EmployeeCapacity.EmployeeCapacityId == id, 
        models.EmployeeCapacity.EntityStatus != "Archived" # Only update active records
    ).first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee Capacity record not found or archived")

    # 3. Perform Full Update (Replace all fields using payload data)
    update_data = payload.dict() # Use .dict() for PUT, as all fields must be present
    
    for key, value in update_data.items():
        # Prevent client from trying to overwrite the ID
        if key == "EmployeeCapacityId":
             continue
        setattr(obj, key, value)
        
    # Set audit fields
    if hasattr(obj, 'UpdatedAt'):
        obj.UpdatedAt = now() 
    
    # Also update the EmployeeId if the PUT payload changed it (which is acceptable for a full replacement)
    # obj.EmployeeId = payload.EmployeeId # Example of explicit update if needed

    db.commit()
    db.refresh(obj)

    # 4. Audit Log
    crud.audit_log(
        db, 
        'EmployeeCapacity', 
        obj.EmployeeCapacityId, 
        'Update (PUT)', 
        changed_by=current_user.UserId 
    )
    
    return obj
=======
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
