from datetime import datetime
from sqlalchemy import (
    Column, String, Date, DateTime, Text, Integer, DECIMAL, TIMESTAMP, Numeric,
    ForeignKey, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def now():
    return datetime.utcnow()

# --- Models ---

class Issue(Base):
    __tablename__ = "issue"

    IssueId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey("deliverable.DeliverableId"), nullable=False)
    Title = Column(String(150), nullable=False)
    Description = Column(Text, nullable=True)
    ActionOwnerId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    Priority = Column(String(50), nullable=True)

    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    EntityStatus = Column(String(50), default="Active")

    # Relationships
    action_owner = relationship("Employee", back_populates="owned_issues", foreign_keys=[ActionOwnerId])
    deliverable = relationship("Deliverable", back_populates="issues")

    activities = relationship(
        "IssueActivity",
        back_populates="issue",
        cascade="all, delete-orphan",
        order_by="IssueActivity.CreatedAt"
    )

class IssueActivity(Base):
    __tablename__ = "issue_activity"

    IssueActivityId = Column(String(50), primary_key=True, index=True)
    IssueId = Column(String(50), ForeignKey("issue.IssueId"), nullable=False)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    ActivityDate = Column(DateTime(timezone=True), nullable=True)
    Status = Column(String(50), nullable=True)
    Comment = Column(Text, nullable=True)

    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    issue = relationship("Issue", back_populates="activities")
    employee = relationship("Employee", back_populates="issue_activities")

class DeliveryRating(Base):
    __tablename__ = "delivery_rating"

    RatingId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey("deliverable.DeliverableId", ondelete="CASCADE"), nullable=False)
    AttributeId = Column(String(50), ForeignKey("rating_attribute_master.AttributeId"), nullable=False)
    RatedForId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    RatedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    Score = Column(DECIMAL(4, 2), CheckConstraint("Score BETWEEN 0 AND 5"))
    Comment = Column(Text, nullable=True)
    CreatedAt = Column(TIMESTAMP, default=now)
    UpdatedAt = Column(TIMESTAMP, default=now, onupdate=now)

    deliverable = relationship("Deliverable")
    rated_for = relationship("Employee", foreign_keys=[RatedForId])
    rated_by = relationship("Employee", foreign_keys=[RatedById])

class EmployeeCapacity(Base):
    __tablename__ = "employee_capacity"

    EmployeeCapacityId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    BUId = Column(String(50), ForeignKey("business_unit.BUId"), nullable=False)
    CapacityPerDayHours = Column(DECIMAL(4, 1), CheckConstraint("CapacityPerDayHours > 0"))
    Location = Column(String(100), nullable=True)
    CreatedAt = Column(TIMESTAMP, default=now)
    UpdatedAt = Column(TIMESTAMP, default=now, onupdate=now)

    employee = relationship("Employee")
    business_unit = relationship("BusinessUnit")

class RatingAttributeMaster(Base):
    __tablename__ = "rating_attribute_master"

    AttributeId = Column(String(50), primary_key=True, index=True)
    AttributeName = Column(String(100), nullable=False)
    Description = Column(Text, nullable=True)
    Weight = Column(DECIMAL(5, 2), CheckConstraint("Weight >= 0"), default=1.0)
    CreatedAt = Column(TIMESTAMP, default=now)
    UpdatedAt = Column(TIMESTAMP, default=now, onupdate=now)
    EntityStatus = Column(String(50), default="Active", nullable=False)

class EmployeeLeave(Base):
    __tablename__ = "employee_leave"

    LeaveId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    LeaveDate = Column(Date, nullable=False)
    LeaveType = Column(String(50), nullable=True)
    Reason = Column(Text, nullable=True)
    ApprovedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    Status = Column(String(50), CheckConstraint("Status IN ('Pending','Approved','Rejected')"), nullable=True)
    CreatedAt = Column(TIMESTAMP, default=now)
    UpdatedAt = Column(TIMESTAMP, default=now, onupdate=now)

    employee = relationship("Employee", foreign_keys=[EmployeeId], back_populates="employee_leaves")
    approved_by = relationship("Employee", foreign_keys=[ApprovedById], back_populates="approved_leaves")

class Role:
    TEAM_MEMBER = "TEAM MEMBER"
    PROJECT_MANAGER = "PROJECT MANAGER"
    BU_HEAD = "BU HEAD"
    DEVELOPER = "DEVELOPER"
    DELIVERY_MANAGER = "DELIVERY MANAGER"
    ADMIN = "ADMIN"
    REVIEWER = "REVIEWER"

class RoleMaster(Base):
    __tablename__ = "role_master"

    RoleId = Column(String(50), primary_key=True, index=True)
    RoleName = Column(String(200), unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class DailyStatus(Base):
    __tablename__ = "dailystatus"

    DailyStatusId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey("deliverable.DeliverableId"), nullable=False, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True, index=True)
    WorkDate = Column(Date, nullable=False)
    HoursSpent = Column(Numeric(5, 2), nullable=True)
    Progress = Column(Numeric(5, 2), nullable=True)
    Comment = Column(Text, nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    EntityStatus = Column(String(20), default="Active", nullable=False)

    deliverable = relationship("Deliverable", back_populates="dailystatuses")
    employee = relationship("Employee", back_populates="dailystatuses")

class User(Base):
    __tablename__ = "user"

    UserId = Column(String(50), primary_key=True, index=True)
    userName = Column(String(200), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)

    RoleId = Column(String(50), ForeignKey("role_master.RoleId"), nullable=True)
    role = relationship("RoleMaster", back_populates="users")

    BUId = Column(String(50), ForeignKey("business_unit.BUId"), nullable=False)
    business_unit = relationship("BusinessUnit", back_populates="users")

    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    employee = relationship("Employee", back_populates="user")

    otp = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    emailID = Column(String(200), nullable=True)
    FirstName = Column(String(100), nullable=True)
    lastName = Column(String(100), nullable=True)
    fullName = Column(String(200), nullable=True)

    @property
    def role_name(self):
        return self.role.RoleName if self.role else None

    @property
    def projects_managed(self):
        if self.employee:
            return self.employee.projects_managed
        return []

class BusinessUnit(Base):
    __tablename__ = "business_unit"

    BUId = Column(String(50), primary_key=True, index=True)
    BUName = Column(String(200), nullable=False)
    Description = Column(Text, nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

    users = relationship("User", back_populates="business_unit")
    employees = relationship("Employee", back_populates="business_unit")
    projects = relationship("Project", back_populates="business_unit")
    deliverables = relationship("Deliverable", back_populates="business_unit")

class Project(Base):
    __tablename__ = "project"

    ProjectId = Column(String(50), primary_key=True, index=True)
    BUId = Column(String(50), ForeignKey("business_unit.BUId"), nullable=False)
    ProjectName = Column(String(200), nullable=False)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    CreatedById = Column(String(50), ForeignKey("user.UserId"), nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)

    # Correct way to reference the Delivery Manager via their ID
    DeliveryManagerId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)

    # Relationships
    # Link to the User who created the project
    CreatedBy = relationship("User", foreign_keys=[CreatedById])
    
    # Link to the Business Unit
    business_unit = relationship("BusinessUnit", back_populates="projects")
    
    # Link to the Deliverables for this project
    deliverables = relationship("Deliverable", back_populates="project")
    
    # Link to the Milestones for this project
    milestone = relationship("Milestone", back_populates="project")

    # Correct relationship to the Delivery Manager employee
    delivery_manager = relationship(
        "Employee", 
        back_populates="projects_managed", 
        foreign_keys=[DeliveryManagerId]
    )



class Deliverable(Base):
    __tablename__ = "deliverable"

    DeliverableId = Column(String(50), primary_key=True, index=True)
    ProjectId = Column(String(50), ForeignKey("project.ProjectId"), nullable=False)
    Title = Column(String(300), nullable=False)
    Description = Column(String(500), nullable=True)
    Priority = Column(String(50), nullable=True)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    BUId = Column(String(50), ForeignKey("business_unit.BUId"), nullable=False)
    ProjectManagerId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)

    dailystatuses = relationship("DailyStatus", back_populates="deliverable")
    project = relationship("Project", back_populates="deliverables")
    business_unit = relationship("BusinessUnit", back_populates="deliverables")
    project_manager = relationship("Employee", foreign_keys=[ProjectManagerId])
    reviews = relationship("Review", back_populates="deliverable")
    issues = relationship("Issue", back_populates="deliverable", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="deliverable")


class TaskTypeMaster(Base):
    __tablename__ = "tasktypemaster"

    TaskTypeId = Column(String(50), primary_key=True, index=True)
    TaskTypeName = Column(String(150), nullable=False)

from sqlalchemy import Column, String, ForeignKey, Date, DateTime, Text

class Task(Base):
    __tablename__ = "task"

    TaskId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey("deliverable.DeliverableId"), nullable=True)
    Title = Column(String(150), nullable=False)
    Description = Column(Text, nullable=True)
    Priority = Column(String(50), nullable=True)
    AssignedToId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)  # This FK is critical
    ReviewerId = Column(String(50), nullable=True)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)
    deliverable = relationship("Deliverable", back_populates="tasks")
    assigned_to = relationship("Employee", back_populates="assigned_tasks", foreign_keys=[AssignedToId])



class HolidayCalendar(Base):
    __tablename__ = "holidaycalendar"

    HolidayCalendarId = Column(String(50), primary_key=True, index=True)
    CalendarName = Column(String(100), nullable=True)
    Description = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

class CertificationMaster(Base):
    __tablename__ = "certificationmaster"

    CertificationId = Column(String(50), primary_key=True, index=True)
    CertificationName = Column(String(150), nullable=False)

class Employee(Base):
    __tablename__ = "employee"

    EmployeeId = Column(String(50), primary_key=True, index=True)
    BUId = Column(String(50), ForeignKey("business_unit.BUId"), nullable=True)
    FirstName = Column(String(50), nullable=True)
    LastName = Column(String(50), nullable=True)
    Email = Column(String(50), nullable=True)
    Phone = Column(String(15), nullable=True)
    EntityStatus = Column(String(50), default="Active")

    owned_issues = relationship(
        "Issue",
        back_populates="action_owner",
        foreign_keys="[Issue.ActionOwnerId]"
    )
    issue_activities = relationship(
        "IssueActivity",
        back_populates="employee",
        foreign_keys="[IssueActivity.EmployeeId]"
    )
    employee_leaves = relationship(
        "EmployeeLeave",
        back_populates="employee",
        foreign_keys="[EmployeeLeave.EmployeeId]"
    )
    approved_leaves = relationship(
        "EmployeeLeave",
        back_populates="approved_by",
        foreign_keys="[EmployeeLeave.ApprovedById]"
    )
    certifications = relationship(
        "EmployeeCertification",
        back_populates="employee"
    )
    dailystatuses = relationship(
        "DailyStatus",
        back_populates="employee"
    )
    user = relationship("User", back_populates="employee", uselist=False)
    business_unit = relationship("BusinessUnit", back_populates="employees")
    #assigned_tasks = relationship("Task", back_populates="assigned_to")
    assigned_tasks = relationship("Task", back_populates="assigned_to")

    projects_managed = relationship(
        "Project", 
        back_populates="delivery_manager", 
        foreign_keys="[Project.DeliveryManagerId]"
    )

class Milestone(Base):
    __tablename__ = "milestone"

    MilestoneId = Column(String(50), primary_key=True, index=True)
    ProjectId = Column(String(50), ForeignKey("project.ProjectId"), nullable=False)
    Name = Column(String(150), nullable=False)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    Status = Column(String(50), nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)

    project = relationship("Project", back_populates="milestone")
    deliverables = relationship("DeliverableMilestoneMapping", back_populates="milestone")

    @property
    def Title(self):
        return self.Name

class DeliverableMilestoneMapping(Base):
    __tablename__ = "deliverable_milestone_mapping"

    DeliverableMilestoneMappingId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey("deliverable.DeliverableId"), nullable=False)
    MilestoneId = Column(String(50), ForeignKey("milestone.MilestoneId"), nullable=False)

    deliverable = relationship("Deliverable")
    milestone = relationship("Milestone", back_populates="deliverables")

class SkillMaster(Base):
    __tablename__ = "skillmaster"

    SkillId = Column(String(50), primary_key=True)
    SkillName = Column(String(100), nullable=False)
    SkillLevel = Column(String(50))
    Description = Column(Text)
    CreatedAt = Column(TIMESTAMP, default=datetime.utcnow)
    UpdatedAt = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskSkillRequirement(Base):
    __tablename__ = "task_skill_requirement"

    TaskSkillRequirementId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50), ForeignKey("task.TaskId"), nullable=False)
    SkillId = Column(String(50), ForeignKey("skillmaster.SkillId"), nullable=False)
    Importance = Column(String(50), nullable=True)

    # Relationships (optional, if needed elsewhere)
    task = relationship("Task", backref="skill_requirements")
    skill = relationship("SkillMaster", backref="task_requirements")

class FeedbackCategoryMaster(Base):
    __tablename__ = "feedback_category_master"

    FeedbackCategoryId = Column(String(50), primary_key=True, index=True)
    CategoryName = Column(String(255), nullable=False)
    CreatedAt = Column(String(50), default=now)
    UpdatedAt = Column(String(50), default=now, onupdate=now)
    EntityStatus = Column(String(50), default="Active")

class EmployeeCertification(Base):
    __tablename__ = "employee_certification"

    EmployeeCertificationId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    CertificationName = Column(String(200), nullable=False)
    Institution = Column(String(200), nullable=True)
    CertificationDate = Column(Date, nullable=True)
    ExpiryDate = Column(Date, nullable=True)
    CertificationNumber = Column(String(100), nullable=True)
    CertificationType = Column(String(100), nullable=True)
    CertificationScore = Column(DECIMAL(5, 2), nullable=True)
    CreatedAt = Column(DateTime, default=now)

    employee = relationship("Employee", back_populates="certifications")

# --- Review and related discussion models ---

class Review(Base):
    __tablename__ = "review"

    ReviewId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey("deliverable.DeliverableId"), nullable=False)
    ReviewType = Column(String(50), nullable=True)
    ReviewStatus = Column(String(50), nullable=True)
    ReviewStartDate = Column(Date, nullable=True)
    ReviewEndDate = Column(Date, nullable=True)
    ReviewerId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    ReviewNotes = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

    deliverable = relationship("Deliverable", back_populates="reviews")
    reviewer = relationship("Employee")
    discussion_threads = relationship(
        "ReviewDiscussionThread",
        back_populates="review",
        cascade="all, delete-orphan"
    )

class ReviewDiscussionThread(Base):
    __tablename__ = "review_discussion_thread"

    ReviewDiscussionThreadId = Column(String(50), primary_key=True, index=True)
    ReviewId = Column(String(50), ForeignKey("review.ReviewId"), nullable=False)
    Title = Column(String(200), nullable=True)
    Description = Column(Text, nullable=True)
    CreatedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

    review = relationship("Review", back_populates="discussion_threads")
    created_by = relationship("Employee")
    comments = relationship(
        "ReviewDiscussionComment",
        back_populates="thread",
        cascade="all, delete-orphan"
    )
    EntityStatus = Column(String(50), default="Active", nullable=False)

class ReviewDiscussionComment(Base):
    __tablename__ = "review_discussion_comment"

    ReviewDiscussionCommentId = Column(String(50), primary_key=True, index=True)
    ReviewDiscussionThreadId = Column(String(50), ForeignKey("review_discussion_thread.ReviewDiscussionThreadId"), nullable=False)
    CommentText = Column(Text, nullable=False)
    CreatedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    CreatedAt = Column(DateTime, default=now)

    thread = relationship("ReviewDiscussionThread", back_populates="comments")
    created_by = relationship("Employee")
    EntityStatus = Column(String(50), default="Active", nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_log"

    AuditLogId = Column(String(50), primary_key=True, index=True)
    UserId = Column(String(50), ForeignKey("user.UserId"), nullable=True)
    Action = Column(String(200), nullable=False)
    TableName = Column(String(100), nullable=True)
    RecordId = Column(String(50), nullable=True)
    Timestamp = Column(DateTime, default=now)
    Details = Column(Text, nullable=True)

    user = relationship("User")



