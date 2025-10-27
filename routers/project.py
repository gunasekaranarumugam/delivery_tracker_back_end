from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from main import models, schemas, crud
from main.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(
        **payload.model_dump(exclude_unset=True),
     
        created_by="SYSTEM",
        updated_by="SYSTEM",
        created_at=datetime.utcnow(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    crud.audit_log(db, "Project", project.project_id, "Create", changed_by="SYSTEM")
    return project



@router.get("/", response_model=List[schemas.ProjectRead])
def list_projects(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    return db.query(models.Project).offset(offset).limit(limit).all()



@router.get("/{id}", response_model=schemas.ProjectRead)
def get_project_by_id(id: str, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.project_id == id).first()
    return project

@router.put("/{id}", response_model=schemas.ProjectRead)
def update_project(id: str, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.project_id == id).first()

    if not project:
        project = models.Project(
            project_id=id,
            **payload.model_dump(exclude_unset=True),
            created_by="SYSTEM",
            updated_by="SYSTEM",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(project)
    else:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        project.updated_by = "SYSTEM"

    db.commit()
    db.refresh(project)

    crud.audit_log(db, "Project", project.project_id, "Update", changed_by="SYSTEM")
    return project


@router.patch("/{id}/archive", response_model=schemas.ProjectRead, status_code=status.HTTP_200_OK)
def patch_project(
    id: str,
    payload: schemas.ProjectPatch,  # schema with optional fields
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.project_id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update only provided fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    # Automatically archive if requested
    if payload.entity_status and payload.entity_status.upper() == "ARCHIVED":
        project.entity_status = "ARCHIVED"

    # Update timestamps and system info
    project.updated_at = datetime.utcnow()
    project.updated_by = "SYSTEM"

    db.commit()
    db.refresh(project)

    # Audit log
    crud.audit_log(
        db,
        entity_type="Project",
        entity_id=project.project_id,
        action="Patch",
        changed_by="SYSTEM"
    )

    return project
