from fastapi import FastAPI
from main.database import Base, engine
from routers import ( 
    user, businessunit, project, deliverable, holidaycalendar,
    rolemaster, employee, employeerole,
    certificationmaster, employeecertification,
    skillmaster, tasktypemaster, task, taskskillrequirement,
    feedbackcategorymaster, review, reviewdiscussionthread, reviewdiscussioncomment,daily_status,
    auditlog, milestone, issue, issue_activity, delivery_rating, employee_capacity, employee_leave,rating_attribute_master
)





# Create tables (for development convenience)
Base.metadata.create_all(bind=engine)

openapi_tags = [
    {"name": "User", "description": "Operations related to system users"},
    {"name": "BusinessUnit", "description": "Manage business units"},
    {"name": "Project", "description": "Create and manage projects"},
    {"name": "Deliverable", "description": "Track project deliverables"},
    {"name": "HolidayCalendar", "description": "Manage holiday calendar"},
    {"name": "RoleMaster", "description": "User role definitions"},
    {"name": "Employee", "description": "Manage employee records"},
    {"name": "CertificationMaster", "description": "Manage certification types"},
    {"name": "EmployeeCertification", "description": "Assign certifications to employees"},
    {"name": "SkillMaster", "description": "Define and manage skills"},
    {"name": "TaskTypeMaster", "description": "Types of tasks"},
    {"name": "Task", "description": "Create and assign tasks"},
    {"name": "TaskSkillRequirement", "description": "Skill requirements for tasks"},
    {"name": "FeedbackCategoryMaster", "description": "Categories for feedback"},
    {"name": "Review", "description": "Review project deliverables"},
    {"name": "ReviewDiscussionThread", "description": "Discussion threads in reviews"},
    {"name": "ReviewDiscussionComment", "description": "Comments on review discussions"},
    {"name": "AuditLog", "description": "System audit logs"},
    {"name": "Milestone", "description": "Manage project milestones"},
    {"name": "Issue", "description": "Track issues related to deliverables"},
    {"name": "IssueActivity", "description": "Track activities on issues"},
    {"name": "EmployeeCapacity", "description": "Manage employee capacity records"},
    {"name": "EmployeeLeave", "description": "Manage employee leave records"},
    {"name": "DeliveryRating", "description": "Manage ratings for deliverables"},
    {"name":"RatingAttributeMaster","description":"Rating of the delivery rating"},
    {"name":"DailyStatus","description":"Status of employee they are working on task"},

]


# FastAPI app instance
app = FastAPI(
    title="Delivery Tracker API",
    description="Simple API for managing delivery tracker tables.",
    version="vFinal19",
    openapi_tags=openapi_tags
)
#app.include_router(user.router, prefix="/user")  # This matters

# Include routers with matching tags
app.include_router(user.router,prefix="/user",tags=["User"])
app.include_router(businessunit.router, prefix="/api/Business", tags=["BusinessUnit"])
app.include_router(project.router, prefix="/api/Projects", tags=["Project"])
app.include_router(milestone.router, prefix="/api/Milestones", tags=["Milestone"])
app.include_router(deliverable.router, prefix="/api/Deliverables", tags=["Deliverable"])
app.include_router(issue.router, prefix="/api/Issues", tags=["Issue"])
app.include_router(issue_activity.router, prefix="/api/IssueActivities", tags=["IssueActivity"])
app.include_router(holidaycalendar.router, prefix="/api/Holidays", tags=["HolidayCalendar"])
app.include_router(rolemaster.router, prefix="/api/Roles", tags=["RoleMaster"])
app.include_router(employee.router, prefix="/api/Employees", tags=["Employee"])
#app.include_router(employeerole.router, prefix="/api/Employee-Roles", tags=["EmployeeRole"])
app.include_router(certificationmaster.router, prefix="/api/Certifications", tags=["CertificationMaster"])
app.include_router(employeecertification.router, prefix="/api/Employee-Certifications", tags=["EmployeeCertification"])
app.include_router(skillmaster.router, prefix="/api/Skills", tags=["SkillMaster"])
app.include_router(tasktypemaster.router, prefix="/api/Task-Types", tags=["TaskTypeMaster"])
app.include_router(task.router, prefix="/api/Tasks", tags=["Task"])
app.include_router(taskskillrequirement.router, prefix="/api/Task-Skill-Reqs", tags=["TaskSkillRequirement"])
app.include_router(feedbackcategorymaster.router, prefix="/api/Feedback-Categories", tags=["FeedbackCategoryMaster"])
app.include_router(review.router, prefix="/api/Reviews", tags=["Review"])
app.include_router(reviewdiscussionthread.router, prefix="/api/Review-Threads", tags=["ReviewDiscussionThread"])
app.include_router(reviewdiscussioncomment.router, prefix="/api/Review-Comments", tags=["ReviewDiscussionComment"])
app.include_router(delivery_rating.router, prefix="/api/DeliveryRatings", tags=["DeliveryRating"])
app.include_router(employee_capacity.router, prefix="/api/EmployeeCapacities", tags=["EmployeeCapacity"])
app.include_router(employee_leave.router, prefix="/api/EmployeeLeaves", tags=["EmployeeLeave"])
#app.include_router(delivery_rating.router, prefix="/api/Delivery-Ratings", tags=["DeliveryRating"])
app.include_router(auditlog.router, prefix="/api/Audit", tags=["AuditLog"])
app.include_router(daily_status.router,prefix="/api/DailyStatus",tags=["DailyStatus"])
app.include_router(rating_attribute_master.router,prefix="/api/RatingAttributeMaster",tags=["RatingAttributeMaster"])
# Root endpoint
@app.get("/")
def root():
    return {"message": "Delivery Tracker API (vFinal19) - running"}
