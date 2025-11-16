from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    auditlog,
    businessunit,
    deliverable,
    employee,
    issue,
    issue_activity,
    project,
    task,
    taskstatus,
    tasktype,
)


openapi_tags = [
    {"name": "Employee", "description": "Manage employee records"},
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
    {"name": "AuditLog", "description": "System audit logs"},
]

app = FastAPI(
    title="Delivery Tracker API",
    description="Simple API for managing delivery tracker tables.",
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
app.include_router(
    businessunit.router, prefix="/api/BusinessUnit", tags=["BusinessUnit"]
)
app.include_router(project.router, prefix="/api/Projects", tags=["Project"])
app.include_router(deliverable.router, prefix="/api/Deliverables", tags=["Deliverable"])
app.include_router(task.router, prefix="/api/Tasks", tags=["Task"])
app.include_router(tasktype.router, prefix="/api/Task-Type", tags=["TaskType"])
app.include_router(taskstatus.router, prefix="/api/Task-Status", tags=["TaskStatus"])
app.include_router(issue.router, prefix="/api/Issues", tags=["Issue"])
app.include_router(
    issue_activity.router, prefix="/api/IssueActivities", tags=["IssueActivity"]
)
app.include_router(auditlog.router, prefix="/api/Audit", tags=["AuditLog"])


@app.get("/")
def root():
    return {"message": "Delivery Tracker API (v1.0) - running"}
