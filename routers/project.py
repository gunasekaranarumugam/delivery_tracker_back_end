from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session

from main import crud, models, schemas
from main.database import get_db

from .employee import get_current_employee


router = APIRouter()


@router.post(
    "/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    project = models.Project(
        **payload.model_dump(exclude_unset=True),
        created_by=current_employee.employee_id,
        updated_by=current_employee.employee_id,
        created_at=datetime.utcnow(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    project_view = (
        db.query(models.ProjectView)
        .filter(models.ProjectView.project_id == project.project_id)
        .first()
    )

    crud.audit_log(db, "Project", project.project_id, "Create", changed_by="SYSTEM")
    return project_view


@router.get("/", response_model=List[schemas.ProjectRead])
def list_projects(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return db.query(models.ProjectView).all()


@router.get("/{id}", response_model=schemas.ProjectRead)
def get_project_by_id(id: str, db: Session = Depends(get_db)):
    project = (
        db.query(models.ProjectView).filter(models.ProjectView.project_id == id).first()
    )
    return project


@router.put("/{id}", response_model=schemas.ProjectRead, status_code=200)
def update_project(
    id: str,
    payload: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    """
    Update project fields in the Project table.
    Return the fully populated ProjectView for frontend display.
    """
    try:
        project = (
            db.query(models.Project).filter(models.Project.project_id == id).first()
        )

        if not project:
            project = models.Project(
                project_id=id,
                **payload.model_dump(exclude_unset=True),
                created_by=current_employee.employee_id,
                updated_by=current_employee.employee_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                entity_status="Active",
            )
            db.add(project)
        else:
            print(
                "Payload fields being updated:", payload.model_dump(exclude_unset=True)
            )

            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(project, key, value)

            project.updated_at = datetime.utcnow()
            project.updated_by = current_employee.employee_id

        db.commit()
        db.refresh(project)

        crud.audit_log(
            db,
            "Project",
            project.project_id,
            "Update",
            changed_by=current_employee.employee_id,
        )

        project_view = (
            db.query(models.ProjectView)
            .filter(models.ProjectView.project_id == project.project_id)
            .first()
        )

        if not project_view:
            raise HTTPException(
                status_code=500, detail="Project updated but view not found"
            )

        print("Updated project table value:", project.delivery_manager_id)
        print(
            "Returned view value:",
            project_view.delivery_manager_id,
            project_view.delivery_manager_name,
        )

        return project_view

        print(project_view.delivery_manager_id, project_view.delivery_manager_name)

    except (IntegrityError, DBAPIError, OperationalError) as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.patch("/{id}/archive")
def archive_project(
    id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(get_current_employee),
):
    project = db.query(models.Project).filter(models.Project.project_id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.entity_status = "ARCHIVED"
    project.updated_at = datetime.utcnow()
    project.updated_by = current_employee.employee_id

    db.commit()
    db.refresh(project)

    return {
        "message": "Project archived successfully",
        "project_id": project.project_id,
    }
