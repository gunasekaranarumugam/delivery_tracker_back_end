from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from main import models, schemas, crud
from main.database import get_db
from .deliverable import get_current_user_from_cookie

router = APIRouter()


@router.post("/", response_model=schemas.DailyStatusRead, summary="Add new Daily Status")
def create_daily_status(
    payload: schemas.DailyStatusCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    allowed_create_roles = [
        models.Role.TEAM_MEMBER,
        models.Role.ADMIN,
        models.Role.BU_HEAD,
        models.Role.DELIVERY_MANAGER,
    ]

    if current_user.role_name not in allowed_create_roles:
        raise HTTPException(status_code=403, detail="Not authorized to create daily status")

    existing = db.query(models.DailyStatus).filter_by(DailyStatusId=payload.DailyStatusId).first()
    if existing:
        raise HTTPException(status_code=400, detail="DailyStatusId already exists")

    deliverable = db.query(models.Deliverable).filter_by(DeliverableId=payload.DeliverableId).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    if payload.EmployeeId:
        employee = db.query(models.Employee).filter_by(EmployeeId=payload.EmployeeId).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

    daily_status = models.DailyStatus(**payload.dict())
    db.add(daily_status)
    db.commit()
    db.refresh(daily_status)

    crud.audit_log(db, "DailyStatus", daily_status.DailyStatusId, "Create", changed_by=current_user.userName)
    return daily_status


@router.get("/", response_model=List[schemas.DailyStatusRead], summary="List Daily Status records")
def list_daily_statuses(
    limit: int = Query(100, ge=1),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    allowed_view_roles = [
        models.Role.ADMIN,
        models.Role.BU_HEAD,
        models.Role.DELIVERY_MANAGER,
        models.Role.PROJECT_MANAGER,
        models.Role.TEAM_MEMBER,
    ]

    if current_user.role_name not in allowed_view_roles:
        raise HTTPException(status_code=403, detail="Not authorized to view daily status")

    query = db.query(models.DailyStatus)

    if current_user.role_name == models.Role.ADMIN or current_user.role_name == models.Role.BU_HEAD or current_user.role_name == models.Role.DELIVERY_MANAGER:
        # Admin, BU Head, Delivery Manager see all records within their BU
        query = query.join(models.Deliverable).filter(models.Deliverable.BUId == current_user.BUId)
    elif current_user.role_name == models.Role.PROJECT_MANAGER:
        # Project Manager: show daily statuses related to their projects
        # Assuming you have a relation: Deliverable.ProjectId or similar
        # This example assumes Deliverable has ProjectId and User has access to ProjectIds list
        # Adjust this logic based on your schema
        
        # For demonstration, let's filter Deliverables in projects managed by current_user:
        managed_projects = [p.ProjectId for p in current_user.projects_managed]  # you need to implement this relation
        query = query.join(models.Deliverable).filter(models.Deliverable.ProjectId.in_(managed_projects))
    else:
        # Team Member: show only their own daily status entries
        query = query.filter(models.DailyStatus.EmployeeId == current_user.UserId)

    return query.offset(offset).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.DailyStatusRead, summary="Get Daily Status by ID")
def get_daily_status(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.DailyStatus).filter(models.DailyStatus.DailyStatusId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="DailyStatus not found")

    if current_user.role_name in [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.DELIVERY_MANAGER]:
        # These roles can view all records within their BU
        deliverable = db.query(models.Deliverable).filter_by(DeliverableId=obj.DeliverableId).first()
        if not deliverable or deliverable.BUId != current_user.BUId:
            raise HTTPException(status_code=403, detail="Not authorized to view this record")
    elif current_user.role_name == models.Role.PROJECT_MANAGER:
        # Check if project manager manages this project (implement your logic)
        deliverable = db.query(models.Deliverable).filter_by(DeliverableId=obj.DeliverableId).first()
        if not deliverable:
            raise HTTPException(status_code=403, detail="Not authorized to view this record")

        if deliverable.ProjectId not in [p.ProjectId for p in current_user.projects_managed]:
            raise HTTPException(status_code=403, detail="Not authorized to view this record")
    else:
        # Team Member can view only their own records
        if obj.EmployeeId != current_user.UserId:
            raise HTTPException(status_code=403, detail="Not authorized to view this record")

    return obj


@router.put("/{item_id}", response_model=schemas.DailyStatusRead, summary="Update Daily Status")
def update_daily_status(
    item_id: str,
    payload: schemas.DailyStatusCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    obj = db.query(models.DailyStatus).filter(models.DailyStatus.DailyStatusId == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="DailyStatus not found")

    # Only Admin, BU Head, Delivery Manager or the owner can update
    if current_user.role_name not in [models.Role.ADMIN, models.Role.BU_HEAD, models.Role.DELIVERY_MANAGER] and obj.EmployeeId != current_user.UserId:
        raise HTTPException(status_code=403, detail="Not authorized to update this record")

    # Validate if DeliverableId is changed
    if payload.DeliverableId != obj.DeliverableId:
        deliverable = db.query(models.Deliverable).filter_by(DeliverableId=payload.DeliverableId).first()
        if not deliverable:
            raise HTTPException(status_code=404, detail="Deliverable not found")

    # Validate if EmployeeId is changed
    if payload.EmployeeId and payload.EmployeeId != obj.EmployeeId:
        employee = db.query(models.Employee).filter_by(EmployeeId=payload.EmployeeId).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

    for k, v in payload.dict().items():
        setattr(obj, k, v)

    obj.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(obj)

    crud.audit_log(db, "DailyStatus", obj.DailyStatusId, "Update", changed_by=current_user.userName)
    return obj


@router.patch("/{item_id}/archive", summary="Archive Daily Status (not implemented)")
def archive_daily_status(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_from_cookie),
):
    raise HTTPException(status_code=501, detail="Archive endpoint not implemented for DailyStatus")
