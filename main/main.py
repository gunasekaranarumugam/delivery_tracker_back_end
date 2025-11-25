from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    business_unit,
    deliverable,
    employee,
    employee_business_unit,
    issue,
    issue_activity,
    login,
    project,
    task,
    task_status,
    task_type,
)


openapi_tags = [
    {"name": "Login", "description": "Authorize"},
    {"name": "Employee", "description": "Manage employee details"},
    {"name": "EmployeeBusinessUnit", "description": "Manage employee business unit"},
    {"name": "BusinessUnit", "description": "Manage business units"},
    {"name": "Project", "description": "Create and manage projects"},
    {"name": "Deliverable", "description": "Track project deliverables"},
    {"name": "Task", "description": "Create and assign tasks"},
    {"name": "TaskType", "description": "Types of tasks"},
    {
        "name": "TaskStatus",
        "description": "Status of employee they are working on task",
    },
    {"name": "Issue", "description": "Track issues related to deliverables"},
    {"name": "IssueActivity", "description": "Track activities on issues"},
]

app = FastAPI(
    title="Delivery Tracker API",
    description="API for managing delivery tracker tables.",
    version="v1.0",
    openapi_tags=openapi_tags,
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee.router, prefix="/api/Employees", tags=["Employee"])
app.include_router(login.router, prefix="/api/login", tags=["Login"])
app.include_router(
    employee_business_unit.router,
    prefix="/api/EmployeesBusinessUnit",
    tags=["EmployeeBusinessUnit"],
)
app.include_router(
    business_unit.router, prefix="/api/BusinessUnit", tags=["BusinessUnit"]
)
app.include_router(project.router, prefix="/api/Projects", tags=["Project"])
app.include_router(deliverable.router, prefix="/api/Deliverables", tags=["Deliverable"])
app.include_router(task.router, prefix="/api/Tasks", tags=["Task"])
app.include_router(task_type.router, prefix="/api/TaskType", tags=["TaskType"])
app.include_router(task_status.router, prefix="/api/TaskStatus", tags=["TaskStatus"])
app.include_router(issue.router, prefix="/api/Issues", tags=["Issue"])
app.include_router(
    issue_activity.router, prefix="/api/IssueActivities", tags=["IssueActivity"]
)


@app.get("/")
def root():
    return {"message": "Delivery Tracker API - running test"}
