from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db
from main.utils import handle_db_error, now_utc

from .employee import get_current_employee


router = APIRouter()


@router.post("/", response_model=schemas.ProjectViewBase)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        project = models.Project(
            **payload.model_dump(),
            created_at=now_utc(),
            created_by=current_employee.employee_id,
            updated_at=now_utc(),
            updated_by=current_employee.employee_id,
            entity_status="Active",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Failed to initialize Project model. "
                f"Check required fields or data types: {e}"
            ),
        )
    try:
        db.add(project)
        db.commit()
        db.refresh(project)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Project creation")
    try:
        crud.audit_log(
            db,
            "Project",
            project.project_id,
            "Create",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        project_view = (
            db.query(models.ProjectView)
            .filter(models.ProjectView.project_id == project.project_id)
            .first()
        )
        return project_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Project view.",
        )


@router.get("/", response_model=List[schemas.ProjectViewBase])
def list_projects(db: Session = Depends(get_db)):
    try:
        project_view = (
            db.query(models.ProjectView)
            .filter(models.ProjectView.entity_status == "Active")
            .all()
        )
        return project_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching created Project view.",
        )


@router.get("/{id}", response_model=schemas.ProjectViewBase)
def get_project_by_id(id: str, db: Session = Depends(get_db)):
    try:
        project_view = (
            db.query(models.ProjectView)
            .filter(models.ProjectView.project_id == id)
            .first()
        )
        if not project_view:
            raise HTTPException(status_code=404, detail="Project not found")
        return project_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching Project details.",
        )


@router.put("/{id}", response_model=schemas.ProjectViewBase)
def update_project(
    id: str,
    payload: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):

    try:
        project = (
            db.query(models.Project).filter(models.Project.project_id == id).first()
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Project for update.",
        )
    try:
        update_data = payload.model_dump()
        for key, value in update_data.items():
            if value is None:
                continue
            if not hasattr(project, key):
                continue
            setattr(project, key, value)
        project.updated_at = now_utc()
        project.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(project)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Project update")
    try:
        crud.audit_log(
            db,
            entity_type="Project",
            entity_id=project.project_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        project_view = (
            db.query(models.ProjectView)
            .filter(models.ProjectView.project_id == id)
            .first()
        )
        return project_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Project after update.",
        )


@router.patch("/{id}/archive", response_model=List[schemas.ProjectViewBase])
def archive_project(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    try:
        project = (
            db.query(models.Project).filter(models.Project.project_id == id).first()
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching Project for update.",
        )
    try:
        project.entity_status = "Archived"
        project.updated_at = now_utc()
        project.updated_by = current_employee.employee_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply update payload: {e}",
        )
    try:
        db.commit()
        db.refresh(project)
    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        handle_db_error(db, e, "Project update")
    try:
        crud.audit_log(
            db,
            entity_type="Project",
            entity_id=project.project_id,
            action="Update",
            changed_by=current_employee.employee_id,
        )
    except Exception:
        pass
    try:
        project_view = (
            db.query(models.ProjectView)
            .filter(models.ProjectView.entity_status == "Active")
            .all()
        )
        return project_view
    except (DBAPIError, OperationalError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while querying Project view after update.",
        )
