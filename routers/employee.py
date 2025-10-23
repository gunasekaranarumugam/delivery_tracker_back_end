from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from sqlalchemy.orm import Session, aliased
from main import models, schemas, crud
from main.database import get_db
from .deliverable import get_current_user_from_cookie  # your auth dependency
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select
router = APIRouter()

# Roles definitions for convenience
ADMIN = "ADMIN"
BU_HEAD = "BU_HEAD"
PROJECT_MANAGER = "PROJECT MANAGER"

@router.post("/", response_model=schemas.EmployeeRead, status_code=status.HTTP_201_CREATED, summary="Add new Employee record.")
def create_employee(
    payload: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [ADMIN, BU_HEAD]:
        raise HTTPException(status_code=403, detail="Not authorized to create employee")

    if not payload.BUId:
        raise HTTPException(status_code=400, detail="BUId is required")

    # Validate Business Unit
    bu = db.query(models.BusinessUnit).filter_by(BUId=payload.BUId).first()
    if not bu:
        raise HTTPException(status_code=400, detail="Invalid BUId")

    # Check if employee already exists
    existing_employee = db.query(models.Employee).filter_by(EmployeeId=payload.EmployeeId).first()
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee with this EmployeeId already exists")

    # Validate HolidayCalendar if provided
    if payload.HolidayCalendarId:
        calendar = db.query(models.HolidayCalendar).filter_by(HolidayId=payload.HolidayCalendarId).first()
        if not calendar:
            raise HTTPException(status_code=400, detail="Invalid HolidayCalendarId")

    # BU access control: BU_HEAD can create employees only within their BU
    if current_user.role_name == BU_HEAD and current_user.BUId != payload.BUId:
        raise HTTPException(status_code=403, detail="Cannot create employee outside your Business Unit")

    obj = models.Employee(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    crud.audit_log(db, 'Employee', getattr(obj, 'EmployeeId'), 'Create', changed_by=current_user.userName)
    return obj


@router.get("/", response_model=List[schemas.EmployeeRead], summary="Get list of Employee records.")
def list_employees(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    q = db.query(models.Employee)

    print("[DEBUG] ROLE NAME:", current_user.role_name)
    print("[DEBUG] Current user:", current_user.UserId, current_user.role_name, current_user.BUId)


    if current_user.role_name == ADMIN:
        # Admin can see all employees
        pass

    elif current_user.role_name == PROJECT_MANAGER:
        # Step 1: Get project IDs where current user is Delivery Manager
        project_ids_subq = db.query(models.Project.ProjectId).filter(
            models.Project.DeliveryManagerId == current_user.UserId
        ).subquery()

        project_id_select = select(project_ids_subq)

        # Alias Deliverable for joining
        DeliverableAlias = aliased(models.Deliverable)

        # Employees assigned to tasks in those projects
        employees_from_tasks = db.query(models.Employee.EmployeeId).join(
            models.Task, models.Task.AssignedToId == models.Employee.EmployeeId
        ).join(
            DeliverableAlias, models.Task.DeliverableId == DeliverableAlias.DeliverableId
        ).filter(
            DeliverableAlias.ProjectId.in_(project_id_select)
        )

        # Employees who are Project Managers of deliverables in those projects
        employees_from_deliverables = db.query(models.Employee.EmployeeId).join(
            DeliverableAlias, DeliverableAlias.ProjectManagerId == models.Employee.EmployeeId
        ).filter(
            DeliverableAlias.ProjectId.in_(project_id_select)
        )

        # Union of all allowed employee IDs
        allowed_employee_ids_subq = employees_from_tasks.union(
            employees_from_deliverables
        ).subquery()

        allowed_employee_ids_select = select(allowed_employee_ids_subq)

        q = q.filter(models.Employee.EmployeeId.in_(allowed_employee_ids_select))

    else:
        # All other roles see only employees from their own BU
        q = q.filter(models.Employee.BUId == current_user.BUId)

    return q.offset(offset).limit(limit).all()


@router.get("/{employee_id}", response_model=schemas.EmployeeRead, summary="Get Employee by ID.")
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.Employee).get(employee_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")

    if current_user.role_name == ADMIN:
        return obj

    if current_user.role_name == PROJECT_MANAGER:
        project_ids = db.query(models.Project.ProjectId).filter(
            models.Project.DeliveryManagerId == current_user.UserId
        ).subquery()

        employees_from_tasks = db.query(models.Employee.EmployeeId).join(
            models.Task, models.Task.AssignedToId == models.Employee.EmployeeId
        ).join(
            models.Deliverable, models.Task.DeliverableId == models.Deliverable.DeliverableId
        ).filter(
            models.Deliverable.ProjectId.in_(project_ids)
        )

        employees_from_deliverables = db.query(models.Employee.EmployeeId).join(
            models.Deliverable, models.Deliverable.ProjectManagerId == models.Employee.EmployeeId
        ).filter(
            models.Deliverable.ProjectId.in_(project_ids)
        )

        allowed_employee_ids = employees_from_tasks.union(employees_from_deliverables).subquery()
        allowed_ids = [row[0] for row in db.query(allowed_employee_ids).all()]
        if obj.EmployeeId not in allowed_ids:
            raise HTTPException(status_code=403, detail="Not authorized to view this employee")

        return obj

    # Other roles can only view employees in their BU
    if obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Not authorized to view this employee")

    return obj


@router.put("/{employee_id}", response_model=schemas.EmployeeRead, summary="Update Employee record.")
def update_employee(
    employee_id: str,
    payload: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [ADMIN, BU_HEAD]:
        raise HTTPException(status_code=403, detail="Not authorized to update employee")

    obj = db.query(models.Employee).get(employee_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")

    # BU_HEAD can update only employees in their BU
    if current_user.role_name == BU_HEAD and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot update employee outside your Business Unit")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    crud.audit_log(db, 'Employee', getattr(obj, 'EmployeeId'), 'Update', changed_by=current_user.userName)
    return obj


@router.patch("/{employee_id}/archive", summary="Archive Employee record.")
def archive_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    if current_user.role_name not in [ADMIN, BU_HEAD]:
        raise HTTPException(status_code=403, detail="Not authorized to archive employee")

    obj = db.query(models.Employee).get(employee_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")

    if current_user.role_name == BU_HEAD and obj.BUId != current_user.BUId:
        raise HTTPException(status_code=403, detail="Cannot archive employee outside your Business Unit")

    obj.EntityStatus = "Archived"
    db.commit()
    crud.audit_log(db, 'Employee', getattr(obj, 'EmployeeId'), 'Archive', changed_by=current_user.userName)
    return {"status": "archived"}
