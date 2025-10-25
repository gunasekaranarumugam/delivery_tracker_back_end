# schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date  # date and datetime are correctly available

# Utility default for timestamps
def utcnow():
    return datetime.utcnow()


# =====================================================
# === User Schemas ===
# =====================================================

class UserBase(BaseModel):
    UserId: str = Field(..., example="USR-001")
    UserName: str = Field(..., example="john_doe")
    FirstName: Optional[str] = Field(None, example="John")
    lastName: Optional[str] = Field(None, example="Doe")
    emailID: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    password: str = Field(..., example="Secure@123")
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class UserRegister(BaseModel):
    UserName: str = Field(..., example="john_doe")
    password: str = Field(..., example="Secure@123")
    emailID: EmailStr = Field(..., example="john.doe@example.com")
    FirstName: Optional[str] = Field(None, example="John")
    lastName: Optional[str] = Field(None, example="Doe")


class UserLogin(BaseModel):
    UserName: str
    password: str


# -------------------- RESPONSE SCHEMAS --------------------

class UserRead(BaseModel):
    UserId: str
    UserName: str
    emailID: Optional[EmailStr]
    FirstName: Optional[str]
    lastName: Optional[str]
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True


class UserLoginResponse(BaseModel):
    UserId: str
    userName: str
    emailID: Optional[EmailStr]
    FirstName: Optional[str]
    lastName: Optional[str]
    authToken: str


class UserCreate(UserBase):
    """
    #Schema used for creating a new user.
    """
    pass


# =====================================================
# === Business Unit Schemas ===
# =====================================================

class BusinessUnitBase(BaseModel):
    BUId: str = Field(..., example="BU-001")
    BUName: str = Field(..., example="Analytics BU")
    BUHeadId: str = Field(..., example="EMP-001")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class BusinessUnitCreate(BusinessUnitBase):
    pass

# ADDED BusinessUnitUpdate
class BusinessUnitUpdate(BaseModel):
    BUName: Optional[str] = Field(None, example="Analytics BU New")
    BUHeadId: Optional[str] = Field(None, example="EMP-002")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class BusinessUnitRead(BusinessUnitBase):
    class Config:
        orm_mode = True


# =====================================================
# === Project Schemas ===
# =====================================================

class ProjectBase(BaseModel):
    ProjectId: str = Field(..., example="PRJ-001")
    BUId: str = Field(..., example="BU-001")
    ProjectName: str = Field(..., example="Project Alpha")
    Description: Optional[str] = None
    DeliveryManagerId: str = Field(..., example="EMP-002")
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class ProjectCreate(ProjectBase):
    pass

# ADDED ProjectUpdate
class ProjectUpdate(BaseModel):
    ProjectName: Optional[str] = None
    Description: Optional[str] = None
    DeliveryManagerId: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class ProjectRead(ProjectBase):
    class Config:
        orm_mode = True


# =====================================================
# === Deliverable Schemas ===
# =====================================================

class DeliverableBase(BaseModel):
    DeliverableId: str = Field(..., example="DEL-001")
    ProjectId: str = Field(..., example="PRJ-001")
    Title: str = Field(..., example="UI Module Delivery")
    Description: Optional[str] = None
    Priority: Optional[str] = Field(None, example="High")
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class DeliverableCreate(DeliverableBase):
    pass

# ADDED DeliverableUpdate
class DeliverableUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    Priority: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class DeliverableRead(DeliverableBase):
    class Config:
        orm_mode = True


# =====================================================
# === Milestone Schemas ===
# =====================================================

class MilestoneBase(BaseModel):
    MilestoneId: str = Field(..., example="MIL-001")
    ProjectId: str = Field(..., example="PRJ-001")
    Title: str = Field(..., example="Phase 1 Completion")
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)

class MilestoneCreate(MilestoneBase):
    """Schema used for creating a new Milestone."""
    pass

# ADDED MilestoneUpdate
class MilestoneUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class MilestoneRead(MilestoneBase):
    """Schema used for reading Milestone data (response model)."""
    class Config:
        orm_mode = True


# =====================================================
# === Holiday Calendar Schemas ===
# =====================================================

class HolidayCalendarBase(BaseModel):
    HolidayCalendarId: str = Field(..., example="HC-001")
    CalendarName: Optional[str] = Field(None, example="India Public Holidays")
    Description: Optional[str] = Field(None, example="All official holidays for India region")
    EntityStatus: Optional[str] = Field("Active", example="Active")
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class HolidayCalendarCreate(HolidayCalendarBase):
    """Used for creating a new Holiday Calendar."""
    pass

# ADDED HolidayCalendarUpdate
class HolidayCalendarUpdate(BaseModel):
    CalendarName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class HolidayCalendarRead(HolidayCalendarBase):
    """Used for reading Holiday Calendar data (response model)."""
    class Config:
        orm_mode = True


# =====================================================
# === Holiday Schemas ===
# =====================================================

class HolidayBase(BaseModel):
    HolidayId: str = Field(..., example="HOL-001")
    HolidayCalendarId: str = Field(..., example="HC-001")
    Date: date = Field(..., example="2025-01-26")
    HolidayName: str = Field(..., example="Republic Day")
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class HolidayCreate(HolidayBase):
    """Used for creating a new Holiday entry."""
    pass

# ADDED HolidayUpdate
class HolidayUpdate(BaseModel):
    Date: Optional[date] = None
    HolidayName: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class HolidayRead(HolidayBase):
    """Used for reading Holiday data (response model)."""
    class Config:
        orm_mode = True


# =====================================================
# === Role Master Schemas ===
# =====================================================

class RoleMasterBase(BaseModel):
    RoleId: str = Field(..., example="ROLE-001")
    RoleName: str = Field(..., example="Developer")
    Description: Optional[str] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class RoleMasterCreate(RoleMasterBase):
    pass

# ADDED RoleMasterUpdate
class RoleMasterUpdate(BaseModel):
    RoleName: Optional[str] = None
    Description: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class RoleMasterRead(RoleMasterBase):
    class Config:
        orm_mode = True


# =====================================================
# === Employee Schemas ===
# =====================================================

class EmployeeBase(BaseModel):
    EmployeeId: str = Field(..., example="EMP-001")
    FullName: str = Field(..., example="Alice Developer")
    Email: Optional[str] = Field(None, example="alice@example.com")
    BUId: Optional[str] = Field(None, example="BU-001")
    Status: Optional[str] = "Active"
    HolidayCalendarId: Optional[str] = Field(None, example="HC-001")
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeCreate(EmployeeBase):
    pass

# ADDED EmployeeUpdate
class EmployeeUpdate(BaseModel):
    FullName: Optional[str] = None
    Email: Optional[str] = None
    BUId: Optional[str] = None
    Status: Optional[str] = None
    HolidayCalendarId: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeRead(EmployeeBase):
    class Config:
        orm_mode = True


# =====================================================
# === Employee Role Schemas ===
# =====================================================

class EmployeeRoleBase(BaseModel):
    EmployeeRoleId: str = Field(..., example="ER-001")
    EmployeeId: str = Field(..., example="EMP-001")
    RoleId: str = Field(..., example="ROLE-001")
    Active: Optional[bool] = True
    AssignedDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeRoleCreate(EmployeeRoleBase):
    pass

# ADDED EmployeeRoleUpdate
class EmployeeRoleUpdate(BaseModel):
    RoleId: Optional[str] = None
    Active: Optional[bool] = None
    AssignedDate: Optional[date] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeRoleRead(EmployeeRoleBase):
    class Config:
        orm_mode = True

# =====================================================
# === Certification Master Schemas ===
# =====================================================

class CertificationMasterBase(BaseModel):
    CertificationId: str = Field(..., example="CERT-001")
    CertificationName: str = Field(..., example="AWS Developer Associate")
    SkillId: str = Field(..., example="SK-001")
    IssuingAuthority: Optional[str] = Field(None, example="Amazon")
    ValidDurationDays: Optional[int] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class CertificationMasterCreate(CertificationMasterBase):
    pass

# ADDED CertificationMasterUpdate
class CertificationMasterUpdate(BaseModel):
    CertificationName: Optional[str] = None
    SkillId: Optional[str] = None
    IssuingAuthority: Optional[str] = None
    ValidDurationDays: Optional[int] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class CertificationMasterRead(CertificationMasterBase):
    class Config:
        orm_mode = True


# =====================================================
# === Employee Certification Schemas ===
# =====================================================

class EmployeeCertificationBase(BaseModel):
    EmployeeCertificationId: str = Field(..., example="EC-001")
    EmployeeId: str = Field(..., example="EMP-001")
    CertificationId: str = Field(..., example="CERT-001")
    IssuedDate: Optional[date] = None
    CertificationNumber: Optional[str] = Field(None, example="ABC123")
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeCertificationCreate(EmployeeCertificationBase):
    pass

# ADDED EmployeeCertificationUpdate
class EmployeeCertificationUpdate(BaseModel):
    CertificationId: Optional[str] = None
    IssuedDate: Optional[date] = None
    CertificationNumber: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeCertificationRead(EmployeeCertificationBase):
    class Config:
        orm_mode = True


# =====================================================
# === Skill Master Schemas ===
# =====================================================

class SkillMasterBase(BaseModel):
    SkillId: str = Field(..., example="SK-001")
    SkillName: str = Field(..., example="Python")
    SkillLevel: Optional[str] = Field(None, example="Expert")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class SkillMasterCreate(SkillMasterBase):
    pass

# ADDED SkillMasterUpdate
class SkillMasterUpdate(BaseModel):
    SkillName: Optional[str] = None
    SkillLevel: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class SkillMasterRead(SkillMasterBase):
    class Config:
        orm_mode = True


# =====================================================
# === Task Type Master Schemas ===
# =====================================================

class TaskTypeMasterBase(BaseModel):
    TaskTypeId: str = Field(..., example="TT-001")
    TaskTypeName: str = Field(..., example="Development")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class TaskTypeMasterCreate(TaskTypeMasterBase):
    pass

# ADDED TaskTypeMasterUpdate
class TaskTypeMasterUpdate(BaseModel):
    TaskTypeName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class TaskTypeMasterRead(TaskTypeMasterBase):
    class Config:
        orm_mode = True


# =====================================================
# === Task Schemas ===
# =====================================================

class TaskBase(BaseModel):
    TaskId: str = Field(..., example="TASK-001")
    DeliverableId: str = Field(..., example="DEL-001")
    TaskTypeId: str = Field(..., example="TT-001")
    Title: str = Field(..., example="Develop API Endpoint")
    Description: Optional[str] = None
    AssignedToId: Optional[str] = Field(None, example="EMP-002")
    ReviewerId: Optional[str] = Field(None, example="EMP-003")
    Priority: Optional[str] = Field(None, example="High")
    PlannedStartDate: Optional[date] = None
    EstimatedHours: Optional[float] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class TaskCreate(TaskBase):
    pass

# ADDED TaskUpdate
class TaskUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    AssignedToId: Optional[str] = None
    ReviewerId: Optional[str] = None
    Priority: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    EstimatedHours: Optional[float] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class TaskRead(TaskBase):
    class Config:
        orm_mode = True


# =====================================================
# === Task Skill Requirement Schemas ===
# =====================================================

class TaskSkillRequirementBase(BaseModel):
    TaskSkillRequirementId: str = Field(..., example="TSR-001")
    TaskId: str = Field(..., example="TASK-001")
    SkillId: str = Field(..., example="SK-001")
    Importance: Optional[str] = Field(None, example="High")


class TaskSkillRequirementCreate(TaskSkillRequirementBase):
    pass

# ADDED TaskSkillRequirementUpdate
class TaskSkillRequirementUpdate(BaseModel):
    SkillId: Optional[str] = None
    Importance: Optional[str] = None


class TaskSkillRequirementRead(TaskSkillRequirementBase):
    class Config:
        orm_mode = True


# =====================================================
# === Feedback Category Master Schemas ===
# =====================================================

class FeedbackCategoryMasterBase(BaseModel):
    FeedbackCategoryId: str = Field(..., example="FC-001")
    CategoryName: str = Field(..., example="Code Quality")


class FeedbackCategoryMasterCreate(FeedbackCategoryMasterBase):
    pass

# ADDED FeedbackCategoryMasterUpdate
class FeedbackCategoryMasterUpdate(BaseModel):
    CategoryName: Optional[str] = None


class FeedbackCategoryMasterRead(FeedbackCategoryMasterBase):
    class Config:
        orm_mode = True


# =====================================================
# === Review Schemas ===
# =====================================================

class ReviewBase(BaseModel):
    ReviewId: str = Field(..., example="REV-001")
    TaskId: str = Field(..., example="TASK-001")
    ReviewerId: str = Field(..., example="EMP-003")
    Status: Optional[str] = Field("under review", example="under review")
    VerdictDate: Optional[date] = None
    OverallComments: Optional[str] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class ReviewCreate(ReviewBase):
    pass

# ADDED ReviewUpdate
class ReviewUpdate(BaseModel):
    Status: Optional[str] = None
    VerdictDate: Optional[date] = None
    OverallComments: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class ReviewRead(ReviewBase):
    class Config:
        orm_mode = True


# =====================================================
# === Review Discussion Thread Schemas ===
# =====================================================

class ReviewDiscussionThreadBase(BaseModel):
    DiscussionId: str = Field(..., example="DISC-001")
    ReviewId: str = Field(..., example="REV-001")
    CommenterId: str = Field(..., example="EMP-001")
    CommentRole: Optional[str] = Field("Reviewer", example="Reviewer")
    RemarksText: Optional[str] = Field(None, example="Need to refactor module")
    CommentDate: Optional[date] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class ReviewDiscussionThreadCreate(ReviewDiscussionThreadBase):
    pass

# ADDED ReviewDiscussionThreadUpdate
class ReviewDiscussionThreadUpdate(BaseModel):
    CommentRole: Optional[str] = None
    RemarksText: Optional[str] = None
    CommentDate: Optional[date] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class ReviewDiscussionThreadRead(ReviewDiscussionThreadBase):
    class Config:
        orm_mode = True


# =====================================================
# === Review Discussion Comment Schemas ===
# =====================================================

class ReviewDiscussionCommentBase(BaseModel):
    CommentId: str = Field(..., example="CMT-001")
    ThreadId: str = Field(..., example="DISC-001")
    Comment: str = Field(..., example="Please fix variable naming convention.")


class ReviewDiscussionCommentCreate(ReviewDiscussionCommentBase):
    pass

# ADDED ReviewDiscussionCommentUpdate
class ReviewDiscussionCommentUpdate(BaseModel):
    Comment: Optional[str] = None


class ReviewDiscussionCommentRead(ReviewDiscussionCommentBase):
    class Config:
        orm_mode = True


# =====================================================
# === Audit Log Schemas ===
# =====================================================
# NOTE: Audit logs are typically only created and read, not updated.

class AuditLogBase(BaseModel):
    AuditId: str = Field(..., example="AUD-001")
    EntityType: str = Field(..., example="Task")
    EntityId: str = Field(..., example="TASK-001")
    Action: str = Field(..., example="Update")
    FieldChanged: Optional[str] = None
    OldValue: Optional[str] = None
    NewValue: Optional[str] = None
    ChangedBy: Optional[str] = Field(None, example="EMP-002")
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    class Config:
        orm_mode = True


# =====================================================
# === Daily Status Schemas ===
# =====================================================

class DailyStatusBase(BaseModel):
    DailyStatusId: str = Field(..., example="DS-001")
    TaskId: str = Field(..., example="TASK-001")
    EmployeeId: Optional[str] = Field(None, example="EMP-001")
    WorkDate: date
    HoursSpent: Optional[float] = None
    Progress: Optional[float] = None
    Remarks: Optional[str] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class DailyStatusCreate(DailyStatusBase):
    pass

# ADDED DailyStatusUpdate
class DailyStatusUpdate(BaseModel):
    HoursSpent: Optional[float] = None
    Progress: Optional[float] = None
    Remarks: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class DailyStatusRead(DailyStatusBase):
    class Config:
        orm_mode = True


# =====================================================
# === Issue Schemas ===
# =====================================================

class IssueBase(BaseModel):
    IssueId: str = Field(..., example="ISS-001")
    TaskId: str = Field(..., example="TASK-001")
    Title: str = Field(..., example="API Timeout Issue")
    Description: Optional[str] = None
    ActionOwnerId: Optional[str] = Field(None, example="EMP-001")
    Priority: Optional[str] = Field(None, example="High")
    Status: Optional[str] = Field(None, example="Open")
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class IssueCreate(IssueBase):
    pass

# ADDED IssueUpdate
class IssueUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    ActionOwnerId: Optional[str] = None
    Priority: Optional[str] = None
    Status: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class IssueRead(IssueBase):
    class Config:
        orm_mode = True


# =====================================================
# === Issue Activity Schemas ===
# =====================================================
# NOTE: Issue activities are typically only created and read, not updated.

class IssueActivityBase(BaseModel):
    IssueActivityId: str = Field(..., example="IA-001")
    IssueId: str = Field(..., example="ISS-001")
    EmployeeId: Optional[str] = Field(None, example="EMP-002")
    ActivityDate: Optional[datetime] = None
    Status: Optional[str] = None
    Remarks: Optional[str] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)


class IssueActivityCreate(IssueActivityBase):
    pass


class IssueActivityRead(IssueActivityBase):
    class Config:
        orm_mode = True


# =====================================================
# === Rating Attribute Master Schemas ===
# =====================================================

class RatingAttributeMasterBase(BaseModel):
    AttributeId: str = Field(..., example="RA-001")
    AttributeName: str = Field(..., example="Code Quality")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class RatingAttributeMasterCreate(RatingAttributeMasterBase):
    pass

# ADDED RatingAttributeMasterUpdate
class RatingAttributeMasterUpdate(BaseModel):
    AttributeName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class RatingAttributeMasterRead(RatingAttributeMasterBase):
    class Config:
        orm_mode = True


# =====================================================
# === Delivery Rating Schemas ===
# =====================================================

class DeliveryRatingBase(BaseModel):
    RatingId: str = Field(..., example="RAT-001")
    TaskId: str = Field(..., example="TASK-001")
    AttributeId: str = Field(..., example="RA-001")
    RatedForId: str = Field(..., example="EMP-002")
    RatedById: str = Field(..., example="EMP-003")
    Score: float = Field(..., example=4.5)
    Weight: Optional[float] = Field(None, example=1.0)
    Remarks: Optional[str] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class DeliveryRatingCreate(DeliveryRatingBase):
    pass


class DeliveryRatingUpdate(BaseModel):
    """Schema for updating an existing Delivery Rating. All fields are Optional."""
    TaskId: Optional[str] = Field(None, example="TASK-001")
    AttributeId: Optional[str] = Field(None, example="RA-001")
    RatedForId: Optional[str] = Field(None, example="EMP-002")
    RatedById: Optional[str] = Field(None, example="EMP-003")
    Score: Optional[float] = Field(None, example=4.5)
    Weight: Optional[float] = Field(None, example=1.0)
    Remarks: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class DeliveryRatingRead(DeliveryRatingBase):
    class Config:
        orm_mode = True

# ADDED ALIAS DeliveryRatingOut to fix router import error
class DeliveryRatingOut(DeliveryRatingRead):
    pass


# =====================================================
# === Employee Skill Schemas ===
# =====================================================

class EmployeeSkillBase(BaseModel):
    EmployeeSkillId: str = Field(..., example="ES-001")
    EmployeeId: str = Field(..., example="EMP-001")
    SkillId: str = Field(..., example="SK-001")
    IsPrimary: Optional[bool] = True
    ExperienceYears: Optional[float] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeSkillCreate(EmployeeSkillBase):
    pass

# ADDED EmployeeSkillUpdate
class EmployeeSkillUpdate(BaseModel):
    SkillId: Optional[str] = None
    IsPrimary: Optional[bool] = None
    ExperienceYears: Optional[float] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeSkillRead(EmployeeSkillBase):
    class Config:
        orm_mode = True


# =====================================================
# === Employee Capacity Schemas ===
# =====================================================

class EmployeeCapacityBase(BaseModel):
    EmployeeCapacityId: str = Field(..., example="ECAP-001")
    EmployeeId: str = Field(..., example="EMP-001")
    BUId: str = Field(..., example="BU-001")
    CapacityHours: float = Field(..., example=8.0)
    CapaCityDate: Optional[date] = None
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeCapacityCreate(EmployeeCapacityBase):
    pass


class EmployeeCapacityRead(EmployeeCapacityBase):
    class Config:
        orm_mode = True

# ADDED ALIAS EmployeeCapacityOut to fix router import error
class EmployeeCapacityOut(EmployeeCapacityRead):
    pass

# CORRECTED EmployeeCapacityUpdate
class EmployeeCapacityUpdate(BaseModel):
    """
    Schema for updating an existing Employee Capacity entry.
    All fields are Optional as updates typically only contain fields being changed.
    """
    EmployeeId: Optional[str] = Field(None, example="EMP-001")
    BUId: Optional[str] = Field(None, example="BU-001")
    CapacityHours: Optional[float] = Field(None, example=7.0)
    CapaCityDate: Optional[date] = None
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


# =====================================================
# === Employee Leave Schemas ===
# =====================================================

class EmployeeLeaveBase(BaseModel):
    LeaveId: str = Field(..., example="LEV-001")
    EmployeeId: str = Field(..., example="EMP-001")
    LeaveDate: date
    LeaveType: Optional[str] = Field(None, example="Sick Leave")
    Reason: Optional[str] = None
    ApprovedById: Optional[str] = Field(None, example="EMP-002")
    Status: Optional[str] = Field("Pending", example="Pending")
    CreatedAt: Optional[datetime] = Field(default_factory=utcnow)
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)


class EmployeeLeaveCreate(EmployeeLeaveBase):
    pass


class EmployeeLeaveRead(EmployeeLeaveBase):
    class Config:
        orm_mode = True

# ADDED EmployeeLeaveOut to fix router import error
class EmployeeLeaveOut(EmployeeLeaveRead):
    pass

# CORRECTED EmployeeLeaveUpdate
class EmployeeLeaveUpdate(BaseModel):
    """
    Schema for updating an existing Employee Leave entry.
    All fields are Optional to allow for partial updates.
    """
    EmployeeId: Optional[str] = Field(None, example="EMP-001")
    LeaveDate: Optional[date] = None
    LeaveType: Optional[str] = Field(None, example="Annual Leave")
    Reason: Optional[str] = None
    ApprovedById: Optional[str] = Field(None, example="EMP-002")
    Status: Optional[str] = Field(None, example="Approved")
    UpdatedAt: Optional[datetime] = Field(default_factory=utcnow)
