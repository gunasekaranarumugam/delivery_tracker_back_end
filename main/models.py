from sqlalchemy import Column, String, Integer, Date, DateTime, Text, Boolean, CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

#from main.database import Base
import datetime
from sqlalchemy.types import DECIMAL, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Date

Base = declarative_base()

def now():
    return datetime.datetime.utcnow()


class User(Base):
    __tablename__ = "user"

    UserId = Column(String(50), primary_key=True, index=True)
    UserName = Column(String(100), unique=True, nullable=False)  # <- add this
    FirstName = Column(String(100), nullable=True)
    lastName = Column(String(100), nullable=True)
    emailID = Column(String(200), nullable=True)
    password = Column(String(200), nullable=False)

    @property
    def role_name(self):
        if hasattr(self, "employee") and self.employee and self.employee.role:
                return self.employee.role.RoleName
        return None
    
    

class BusinessUnit(Base):
    __tablename__ = "business_unit"
    BUId = Column(String(50), primary_key=True, index=True)
    BUName = Column(String(200))
    BUHeadId = Column(String(50),ForeignKey('employee.EmployeeId'),nullable=False)
    Description = Column(Text, nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)

class Project(Base):
    __tablename__ = "project"
    ProjectId = Column(String(50), primary_key=True, index=True)
    BUId = Column(String(50), ForeignKey('business_unit.BUId'), nullable=False)
    ProjectName = Column(String(200))
    Description = Column(String(200))
    DeliveryManagerId = Column(String(50),ForeignKey('employee.EmployeeId'),nullable=False)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)

class Deliverable(Base):
    __tablename__ = "deliverable"
    DeliverableId = Column(String(50), primary_key=True, index=True)
    ProjectId = Column(String(50), ForeignKey('project.ProjectId'), nullable=False)
    Title = Column(String(300))
    Description = Column(String(200))
    Priority = Column(String(200))
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)
    


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
    RoleName = Column(String(200))
    Description = Column(String(200))
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)


class Employee(Base):
    __tablename__ = "employee"
    EmployeeId = Column(String(50), primary_key=True, index=True)
    FullName = Column(String(200))
    Email = Column(String(200), index=True)
    BUId = Column(String(50), ForeignKey('business_unit.BUId'), nullable=True)
    Status = Column(String(50), default="Active")
    HolidayCalendarId = Column(String(50), ForeignKey("holidaycalendar.HolidayCalendarId"), nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)

class EmployeeRole(Base):
    __tablename__ = "employee_role"
    EmployeeRoleId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey('employee.EmployeeId'))
    RoleId = Column(String(50), ForeignKey('role_master.RoleId'))
    Active = Column(Boolean, default=True)
    AssignedDate = Column(Date)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)

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



class Task(Base):
    __tablename__ = "task"
    TaskId = Column(String(50), primary_key=True, index=True)
    DeliverableId = Column(String(50), ForeignKey('deliverable.DeliverableId'))
    TaskTypeId = Column(String(50),ForeignKey('task_type_master.TaskTypeId'))
    Title = Column(String(300))
    Description = Column(String(200))
    AssignedToId = Column(String(50), ForeignKey('employee.EmployeeId'), nullable=True)
    ReviewerId = Column(String(50), ForeignKey('employee.EmployeeId'), nullable=True)
    Priority = Column(String(200))
    PlannedStartDate = Column(Date, nullable=True)
    EstimatedHours = Column(DECIMAL(6,2))
    PlannedEndDate = Column(Date, nullable=True)
    EntityStatus = Column(String(50), default="Active")
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now)

class TaskSkillRequirement(Base):
    __tablename__ = "task_skill_requirement"
    TaskSkillRequirementId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50), ForeignKey('task.TaskId'))
    SkillId = Column(String(50), ForeignKey('skill_master.SkillId'))
    Importance = Column(String(50), nullable=True)  # e.g., High/Medium/Low

class FeedbackCategoryMaster(Base):
    __tablename__ = "feedback_category_master"
    FeedbackCategoryId = Column(String(50), primary_key=True, index=True)
    CategoryName = Column(String(200))

class Review(Base):
    __tablename__ = "review"
    ReviewId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50), ForeignKey('task.TaskId'))
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

class AuditLog(Base):
    __tablename__ = "audit_log"
    AuditId = Column(String(80), primary_key=True, index=True)
    EntityType = Column(String(200))
    EntityId = Column(String(200))
    Action = Column(String(100))
    FieldChanged = Column(String(200), nullable=True)
    OldValue = Column(String(1000), nullable=True)
    NewValue = Column(String(1000), nullable=True)
    ChangedBy = Column(String(200), nullable=True)
    CreatedAt = Column(DateTime, default=now)


class DailyStatus(Base):
    __tablename__ = "dailystatus"

    DailyStatusId = Column(String(50), primary_key=True, index=True)
    TaskId = Column(String(50),ForeignKey('task.TaskId'),nullable=False)
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
    TaskId = Column(String(50),ForeignKey('task.TaskId'),nullable=False)
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
    TaskId = Column(String(50), ForeignKey("task.TaskId", ondelete="CASCADE"), nullable=False)
    AttributeId = Column(String(50), ForeignKey("rating_attribute_master.AttributeId"), nullable=False)
    RatedForId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    RatedById = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    Score = Column(DECIMAL(4, 2), CheckConstraint("Score BETWEEN 0 AND 5"))
    Weight = Column(DECIMAL(5,2))
    Remarks = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)

class EmployeeSkill(Base):
    __tablename__ = "employee_skill"

    EmployeeSkillId = Column(String(50),primary_key=True,index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    SkillId = Column(String(50), primary_key=True, index=True)
    IsPrimary = Column(Boolean,default=True)
    ExperienceYears = Column(DECIMAL(4,1))
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)
    EntityStatus = Column(String(50), default="Active", nullable=False)


class EmployeeCapacity(Base):
    __tablename__ = "employee_capacity"

    EmployeeCapacityId = Column(String(50), primary_key=True, index=True)
    EmployeeId = Column(String(50), ForeignKey("employee.EmployeeId"), nullable=False)
    BUId = Column(String(50), ForeignKey("business_unit.BUId"), nullable=False)
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

class Holiday:
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
    ProjectId = Column(String(50), ForeignKey("project.ProjectId", ondelete="CASCADE"), nullable=False)
    Title = Column(String(150), nullable=False)
    Description = Column(Text, nullable=True)
    PlannedStartDate = Column(Date, nullable=True)
    PlannedEndDate = Column(Date, nullable=True)
    CreatedAt = Column(DateTime, default=now)
    UpdatedAt = Column(DateTime, default=now, onupdate=now)






