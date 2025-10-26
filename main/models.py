from sqlalchemy import Column, String, Integer, Date, DateTime, Text, Boolean, CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL, Numeric
import datetime

Base = declarative_base()

def now():
    return datetime.datetime.utcnow()

# ----------------------------------------------------------------------
# Core Models and Relationships
# ----------------------------------------------------------------------

class EmployeeRole(Base):
    __tablename__ = "employee_role"
    employee_role_id = Column(String(10), primary_key=True, index=True)
    employee_role_name = Column(String(100))
    employee_role_description = Column(String(4000))
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10))
    
class Employee(Base):
    __tablename__ = "employee"
    employee_id = Column(String(10), primary_key=True, index=True)
    employee_full_name = Column(String(100))
    employee_email_address = Column(String(100))
    password = Column(String(100))
    business_unit_id = Column(String(10)) 
    holiday_calendar_id = Column(String(10)) 
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10))
    
# ----------------------------------------------------------------------
# Business Unit and Project Models
# ----------------------------------------------------------------------

class BusinessUnit(Base):
    __tablename__ = "business_unit"
    business_unit_id = Column(String(50), primary_key=True, index=True)
    business_unit_name = Column(String(200))
    # FK must refer to 'EmployeeId' as defined in the Employee class
    business_unit_head_id= Column(String(50),ForeignKey('employee.EmployeeId'),nullable=False)
    business_unit_description = Column(Text, nullable=True)
    entity_status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)
    # FK must refer to 'user_id' as defined in the User class
    created_by = Column(String(50),ForeignKey('user.user_id')) 

# Using the new, cleaner snake_case definition for Project
class Project(Base):
    __tablename__ = "project"
    project_id = Column(String(50),primary_key=True,index=True)
    business_unit_id = Column(String(50),ForeignKey('business_unit.business_unit_id'))
    project_name = Column(String(200))
    project_description = Column(String(200))
    # FK must refer to 'EmployeeId' as defined in the Employee class
    delivery_manager_id = Column(String(50),ForeignKey('employee.EmployeeId'))
    # Using 'plan' dates from the provided snake_case version
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    # Added Baseline dates back to the Project model for completeness
    baseline_start_date = Column(DateTime,default=now) 
    baseline_end_date = Column(DateTime,default=now)
    entity_status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)
    created_by = Column(String(50),ForeignKey('user.user_id'))

# Using the new, cleaner snake_case definition for Deliverable
class Deliverable(Base): 
    __tablename__ = "deliverable"
    deliverable_id = Column(String(50),primary_key=True,index=True)
    project_id = Column(String(50),ForeignKey("project.project_id"))
    deliverbale_name = Column(String(50)) # Note: Typo 'deliverbale' in your input kept here
    deliverable_description = Column(String(50))
    priority = Column(String(50))
    baseline_start_date = Column(DateTime,default=now)
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    entity_status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)
    created_by = Column(String(50),ForeignKey('user.user_id'))

# ----------------------------------------------------------------------
# Task and Skill Models
# ----------------------------------------------------------------------

class Role:
    TEAM_MEMBER = "TEAM MEMBER"
    PROJECT_MANAGER = "PROJECT MANAGER"
    BU_HEAD = "BU HEAD"
    DEVELOPER = "DEVELOPER"
    DELIVERY_MANAGER = "DELIVERY MANAGER"
    ADMIN = "ADMIN"
    REVIEWER = "REVIEWER"


class CertificationMaster(Base):
    __tablename__ = "certification_master"
    CertificationId = Column(String(50), primary_key=True, index=True)
    CertificationName = Column(String(200))
    SkillId = Column(String(50),ForeignKey('skill_master.SkillId'),nullable=False)
    IssuingAuthority = Column(String(50))
    ValidDurationDays = Column(Integer)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)


class EmployeeCertification(Base):
    __tablename__ = "employee_certification"
    EmployeeCertificationId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey('employee.EmployeeId'))
    CertificationId = Column(String(50), ForeignKey('certification_master.CertificationId'))
    IssuedDate = Column(Date)
    CertificationNumber = Column(String(100))
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)


class SkillMaster(Base):
    __tablename__ = "skill_master"
    SkillId = Column(String(50), primary_key=True, index=True)
    SkillName = Column(String(200))
    SkillLevel = Column(String(50), nullable=True)
    Description = Column(String(200))
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)


class TaskTypeMaster(Base):
    __tablename__ = "task_type_master"
    TaskTypeId = Column(String(50), primary_key=True, index=True)
    TaskTypeName = Column(String(200))
    Description = Column(String(200))
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)

# Using the new, cleaner snake_case definition for Task
class Task(Base): 
    __tablename__ = "task"

    task_id = Column(String(50), primary_key=True, index=True)
    # FK must refer to 'deliverable_id' as defined in the Deliverable class
    deliverable_id = Column(String(50), ForeignKey('deliverable.deliverable_id')) 
    task_type_id = Column(String(50),ForeignKey('task_type_master.TaskTypeId'))
    task_name = Column(String(300))
    task_description = Column(String(200))
    # FK must refer to 'EmployeeId' as defined in the Employee class
    assigne_id = Column(String(50), ForeignKey('employee.EmployeeId'), nullable=True) 
    reviewer_id = Column(String(50), ForeignKey('employee.EmployeeId'), nullable=True)
    priority = Column(String(200))
    estimated_effort_in_hours = Column(DECIMAL(6,2))
    # Using 'plan' dates from the provided snake_case version
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    # Added Baseline dates back to the Task model for completeness
    baseline_start_date = Column(DateTime,default=now) 
    baseline_end_date = Column(DateTime,default=now)
    entity_status = Column(String(50), default="Active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)
    created_by = Column(String(50),ForeignKey('user.user_id'))


class TaskSkillRequirement(Base):
    __tablename__ = "task_skill_requirement"
    TaskSkillRequirementId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50), ForeignKey('task.task_id')) # Note: This FK still refers to PascalCase PK of Task
    SkillId = Column(String(50), ForeignKey('skill_master.SkillId'))
    Importance = Column(String(50), nullable=True) 

# ----------------------------------------------------------------------
# Review and Audit Models
# ----------------------------------------------------------------------

class FeedbackCategoryMaster(Base):
    __tablename__ = "feedback_category_master"
    FeedbackCategoryId = Column(String(50), primary_key=True, index=True)
    CategoryName = Column(String(200))

class Review(Base):
    __tablename__ = "review"
    ReviewId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50), ForeignKey('task.task_id'))
    ReviewerId = Column(String(50),ForeignKey('employee.EmployeeId'))
    Status = Column(String(50),CheckConstraint("Status IN ('Under Review','Approved','Needs Rework','Rejected','Deferred')"))
    VerdictDate = Column(Date,nullable=True)
    OverallComments = Column(String(500), nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

class ReviewDiscussionThread(Base):
    __tablename__ = "review_discussion_thread"
    DiscussionId = Column(String(50), primary_key=True, index=True)
    ReviewId = Column(String(50), ForeignKey('review.ReviewId'))
    CommenterId = Column(String(50),ForeignKey('employee.EmployeeId'),nullable=False)
    CommentRole = Column(String(50),CheckConstraint("CommentRole IN ('Reviewer','Developer')"))
    RemarksText = Column(String(300))
    CommentDate = Column(Date,nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

class ReviewDiscussionComment(Base):
    __tablename__ = "review_discussion_comment"
    CommentId = Column(String(50), primary_key=True, index=True)
    DiscussionId = Column(String(50), ForeignKey('review_discussion_thread.DiscussionId'))
    Comment = Column(String(1000))

# Using the new, cleaner snake_case definition for AuditLog
class AuditLog(Base): 
    __tablename__ = "audit_log"
    audit_id = Column(String(80), primary_key=True, index=True)
    entity_type = Column(String(200))
    entity_id = Column(String(200))
    action = Column(String(100))
    field_changed = Column(String(200), nullable=True)
    old_value = Column(String(1000), nullable=True)
    new_value = Column(String(1000), nullable=True)
    changed_by = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=now)


# ----------------------------------------------------------------------
# Daily Status, Issues, and Ratings
# ----------------------------------------------------------------------

class DailyStatus(Base):
    __tablename__ = "dailystatus"
    DailyStatusId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50),ForeignKey('task.task_id'),nullable=False)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True, index=True)
    WorkDate = Column(Date, nullable=False)
    HoursSpent = Column(Numeric(5, 2), nullable=True)
    Progress = Column(Numeric(5, 2), nullable=True)
    Remarks = Column(Text, nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class Issue(Base):
    __tablename__ = "issue"

    IssueId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50),ForeignKey('task.task_id'),nullable=False)
    Title = Column(String(150), nullable=False)
    Description = Column(Text, nullable=True)
    ActionOwnerId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    Priority = Column(String(50), nullable=True)
    Status = Column(String(50),nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    UpdatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    

class IssueActivity(Base):
    __tablename__ = "issue_activity"

    IssueActivityId = Column(String(50), primary_key=True, index=True)
    IssueId = Column(String(50), ForeignKey("issue.IssueId"), nullable=False)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    ActivityDate = Column(DateTime(timezone=True), nullable=True)
    Status = Column(String(50), nullable=True)
    Remarks = Column(Text, nullable=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    
class RatingAttributeMaster(Base):
    __tablename__ = "rating_attribute_master"

    AttributeId = Column(String(50), primary_key=True, index=True)
    AttributeName = Column(String(100), nullable=False)
    Description = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)
    EntityStatus = Column(String(50), default="Active", nullable=False)

class DeliveryRating(Base):
    __tablename__ = "delivery_rating"

    RatingId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50), ForeignKey("task.task_id", ondelete="CASCADE"), nullable=False)
    AttributeId = Column(String(50), ForeignKey("rating_attribute_master.AttributeId"), nullable=False)
    RatedForId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    RatedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    Score = Column(DECIMAL(4, 2), CheckConstraint("Score BETWEEN 0 AND 5"))
    Weight = Column(DECIMAL(5,2))
    Remarks = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

# ----------------------------------------------------------------------
# Capacity and Leave Models
# ----------------------------------------------------------------------

class EmployeeSkill(Base):
    __tablename__ = "employee_skill"

    EmployeeSkillId = Column(String(50),primary_key=True,index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    SkillId = Column(String(50), ForeignKey("skill_master.SkillId"), primary_key=True)
    IsPrimary = Column(Boolean,default=True)
    ExperienceYears = Column(DECIMAL(4,1))
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)
    EntityStatus = Column(String(50), default="Active", nullable=False)


class EmployeeCapacity(Base):
    __tablename__ = "employee_capacity"

    EmployeeCapacityId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    BUId = Column(String(50), ForeignKey("business_unit.business_unit_id"), nullable=False) # FK corrected
    CapacityHours = Column(DECIMAL(4, 1), CheckConstraint("CapacityHours > 0"))
    CapaCityDate = Column(Date)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)


class EmployeeLeave(Base):
    __tablename__ = "employee_leave"

    LeaveId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    LeaveDate = Column(Date, nullable=False)
    LeaveType = Column(String(50), nullable=True)
    Reason = Column(Text, nullable=True)
    ApprovedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=True)
    Status = Column(String(50), CheckConstraint("Status IN ('Pending','Approved','Rejected')"), nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

class HolidayCalendar(Base):
    __tablename__ = "holidaycalendar"

    HolidayCalendarId = Column(String(50), primary_key=True, index=True)
    CalendarName = Column(String(100), nullable=True)
    Description = Column(Text, nullable=True)
    EntityStatus = Column(String(50), default="Active", nullable=False)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

class Holiday(Base):
    __tablename__ = "holiday"

    
    HolidayId = Column(String(50), primary_key=True, index=True)
    HolidayCalendarId = Column(String(50),ForeignKey('holidaycalendar.HolidayCalendarId'),nullable=False)
    Date = Column(Date)
    HolidayName = Column(String(50))
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

class Milestone(Base):
    __tablename__ = "milestone"

    MilestoneId = Column(String(50), primary_key=True)
    ProjectId = Column(String(50), ForeignKey("project.project_id", ondelete="CASCADE"), nullable=False) # FK corrected
    Title = Column(String(150), nullable=False)
    Description = Column(Text, nullable=True)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
