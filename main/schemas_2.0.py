from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# Utility default for timestamps
def utcnow():
    return datetime.utcnow()

# =====================================================
# === User Schemas (Based on User model) ===
# NOTE: User model attributes use snake_case
# =====================================================

class UserBase(BaseModel):
    # Mapping to User model: user_id, full_name, email_address, password
    user_id: str = Field(..., example="USR-001")
    full_name: Optional[str] = Field(None, example="John Doe") # Assuming full_name in model
    email_address: EmailStr = Field(..., example="john.doe@example.com") 
    password: str = Field(..., example="Secure@123")
    entitystatus: Optional[str] = Field("Active", example="Active")
    createdat: datetime = Field(default_factory=utcnow)
    updatedat: datetime = Field(default_factory=utcnow)


class UserRegister(BaseModel):
    full_name: str = Field(..., example="John Doe")
    email_address: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure@123")


class UserLogin(BaseModel):
    email_address: EmailStr
    password: str

# -------------------- RESPONSE SCHEMAS --------------------

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    full_name: Optional[str]
    email_address: Optional[EmailStr]
    entitystatus: Optional[str]
    createdat: datetime
    updatedat: datetime


class UserLoginResponse(BaseModel):
    user_id: str
    full_name: Optional[str]
    email_address: Optional[EmailStr]
    authToken: str


class UserCreate(UserBase):
    """Schema used for creating a new user."""
    pass
    
# =====================================================
# === Business Unit Schemas (Based on snake_case model) ===
# =====================================================

class BusinessUnitBase(BaseModel):
    # Mapping to BusinessUnit model: business_unit_id, business_unit_name, etc.
    business_unit_id: str = Field(..., example="BU-001")
    business_unit_name: str = Field(..., example="Analytics BU")
    business_unit_head_id: str = Field(..., example="EMP-001")
    business_unit_description: Optional[str] = None
    entitystatus: Optional[str] = "Active"
    createdat: datetime = Field(default_factory=utcnow)
    updatedat: datetime = Field(default_factory=utcnow)
    createdby: Optional[str] = Field(None, example="USR-001")


class BusinessUnitCreate(BaseModel):
    business_unit_name: str = Field(..., example="Analytics BU")
    business_unit_head_id: str = Field(..., example="EMP-001")
    business_unit_description: Optional[str] = None


class BusinessUnitUpdate(BaseModel):
    business_unit_name: Optional[str] = None
    business_unit_head_id: Optional[str] = None
    business_unit_description: Optional[str] = None
    entitystatus: Optional[str] = None
    updatedat: datetime = Field(default_factory=utcnow)


class BusinessUnitRead(BusinessUnitBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Project Schemas (Based on snake_case model) ===
# =====================================================

class ProjectBase(BaseModel):
    # Mapping to Project model: project_id, business_unit_id, project_name, etc.
    project_id: str = Field(..., example="PRJ-001")
    business_unit_id: str = Field(..., example="BU-001")
    project_name: str = Field(..., example="Project Alpha")
    project_description: Optional[str] = None
    delivery_manager_id: str = Field(..., example="EMP-002")
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    entitystatus: Optional[str] = "Active"
    createdat: datetime = Field(default_factory=utcnow)
    updatedat: datetime = Field(default_factory=utcnow)
    createdby: Optional[str] = Field(None, example="USR-001")


class ProjectCreate(BaseModel):
    business_unit_id: str = Field(..., example="BU-001")
    project_name: str = Field(..., example="Project Alpha")
    project_description: Optional[str] = None
    delivery_manager_id: str = Field(..., example="EMP-002")
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    delivery_manager_id: Optional[str] = None
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    entitystatus: Optional[str] = None
    updatedat: datetime = Field(default_factory=utcnow)


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Deliverable Schemas (Based on snake_case model) ===
# =====================================================

class DeliverableBase(BaseModel):
    # Mapping to Deliverable model: deliverable_id, project_id, deliverbale_name, etc.
    deliverable_id: str = Field(..., example="DEL-001")
    project_id: str = Field(..., example="PRJ-001")
    deliverbale_name: str = Field(..., example="UI Module Delivery") # NOTE: Retaining model's typo
    deliverable_description: Optional[str] = None
    priority: Optional[str] = Field(None, example="High")
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    entitystatus: Optional[str] = "Active"
    createdat: datetime = Field(default_factory=utcnow)
    updatedat: datetime = Field(default_factory=utcnow)
    createdby: Optional[str] = Field(None, example="USR-001")


class DeliverableCreate(BaseModel):
    project_id: str = Field(..., example="PRJ-001")
    deliverbale_name: str = Field(..., example="UI Module Delivery")
    deliverable_description: Optional[str] = None
    priority: Optional[str] = None
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None


class DeliverableUpdate(BaseModel):
    deliverbale_name: Optional[str] = None
    deliverable_description: Optional[str] = None
    priority: Optional[str] = None
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    entitystatus: Optional[str] = None
    updatedat: datetime = Field(default_factory=utcnow)


class DeliverableRead(DeliverableBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Milestone Schemas (Based on PascalCase model) ===
# =====================================================

class MilestoneBase(BaseModel):
    MilestoneId: str = Field(..., example="MIL-001")
    ProjectId: str = Field(..., example="PRJ-001")
    Title: str = Field(..., example="Phase 1 Completion")
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)

class MilestoneCreate(BaseModel):
    ProjectId: str = Field(..., example="PRJ-001")
    Title: str = Field(..., example="Phase 1 Completion")
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None

class MilestoneUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class MilestoneRead(MilestoneBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Holiday Calendar Schemas (PascalCase model) ===
# =====================================================

class HolidayCalendarBase(BaseModel):
    HolidayCalendarId: str = Field(..., example="HC-001")
    CalendarName: Optional[str] = Field(None, example="India Public Holidays")
    Description: Optional[str] = Field(None, example="All official holidays for India region")
    EntityStatus: Optional[str] = Field("Active", example="Active")
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class HolidayCalendarCreate(BaseModel):
    CalendarName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"

class HolidayCalendarUpdate(BaseModel):
    CalendarName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class HolidayCalendarRead(HolidayCalendarBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Holiday Schemas (PascalCase model) ===
# =====================================================

class HolidayBase(BaseModel):
    HolidayId: str = Field(..., example="HOL-001")
    HolidayCalendarId: str = Field(..., example="HC-001")
    Date: date = Field(..., example="2025-01-26")
    HolidayName: str = Field(..., example="Republic Day")
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class HolidayCreate(BaseModel):
    HolidayCalendarId: str = Field(..., example="HC-001")
    Date: date = Field(..., example="2025-01-26")
    HolidayName: str = Field(..., example="Republic Day")

class HolidayUpdate(BaseModel):
    Date: Optional[date] = None
    HolidayName: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class HolidayRead(HolidayBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Role Master Schemas (PascalCase model) ===
# =====================================================

class RoleMasterBase(BaseModel):
    RoleId: str = Field(..., example="ROLE-001")
    RoleName: str = Field(..., example="Developer")
    Description: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class RoleMasterCreate(BaseModel):
    RoleName: str = Field(..., example="Developer")
    Description: Optional[str] = None

class RoleMasterUpdate(BaseModel):
    RoleName: Optional[str] = None
    Description: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class RoleMasterRead(RoleMasterBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Employee Schemas (PascalCase model) ===
# =====================================================

class EmployeeBase(BaseModel):
    EmployeeId: str = Field(..., example="EMP-001")
    FullName: str = Field(..., example="Alice Developer")
    Email: Optional[EmailStr] = Field(None, example="alice@example.com")
    BUId: Optional[str] = Field(None, example="BU-001")
    Status: Optional[str] = "Active"
    HolidayCalendarId: Optional[str] = Field(None, example="HC-001")
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeCreate(BaseModel):
    FullName: str = Field(..., example="Alice Developer")
    Email: EmailStr = Field(..., example="alice@example.com")
    BUId: Optional[str] = Field(None, example="BU-001")
    Status: Optional[str] = "Active"
    HolidayCalendarId: Optional[str] = None

class EmployeeUpdate(BaseModel):
    FullName: Optional[str] = None
    Email: Optional[EmailStr] = None
    BUId: Optional[str] = None
    Status: Optional[str] = None
    HolidayCalendarId: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Employee Role Schemas (PascalCase model) ===
# =====================================================

class EmployeeRoleBase(BaseModel):
    EmployeeRoleId: str = Field(..., example="ER-001")
    EmployeeId: str = Field(..., example="EMP-001")
    RoleId: str = Field(..., example="ROLE-001")
    Active: Optional[bool] = True
    AssignedDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeRoleCreate(BaseModel):
    EmployeeId: str = Field(..., example="EMP-001")
    RoleId: str = Field(..., example="ROLE-001")
    Active: Optional[bool] = True
    AssignedDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"

class EmployeeRoleUpdate(BaseModel):
    RoleId: Optional[str] = None
    Active: Optional[bool] = None
    AssignedDate: Optional[date] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeRoleRead(EmployeeRoleBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Certification Master Schemas (PascalCase model) ===
# =====================================================

class CertificationMasterBase(BaseModel):
    CertificationId: str = Field(..., example="CERT-001")
    CertificationName: str = Field(..., example="AWS Developer Associate")
    SkillId: str = Field(..., example="SK-001")
    IssuingAuthority: Optional[str] = None
    ValidDurationDays: Optional[int] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class CertificationMasterCreate(BaseModel):
    CertificationName: str = Field(..., example="AWS Developer Associate")
    SkillId: str = Field(..., example="SK-001")
    IssuingAuthority: Optional[str] = None
    ValidDurationDays: Optional[int] = None
    EntityStatus: Optional[str] = "Active"

class CertificationMasterUpdate(BaseModel):
    CertificationName: Optional[str] = None
    SkillId: Optional[str] = None
    IssuingAuthority: Optional[str] = None
    ValidDurationDays: Optional[int] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class CertificationMasterRead(CertificationMasterBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Employee Certification Schemas (PascalCase model) ===
# =====================================================

class EmployeeCertificationBase(BaseModel):
    EmployeeCertificationId: str = Field(..., example="EC-001")
    EmployeeId: str = Field(..., example="EMP-001")
    CertificationId: str = Field(..., example="CERT-001")
    IssuedDate: Optional[date] = None
    CertificationNumber: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeCertificationCreate(BaseModel):
    EmployeeId: str = Field(..., example="EMP-001")
    CertificationId: str = Field(..., example="CERT-001")
    IssuedDate: Optional[date] = None
    CertificationNumber: Optional[str] = None
    EntityStatus: Optional[str] = "Active"

class EmployeeCertificationUpdate(BaseModel):
    CertificationId: Optional[str] = None
    IssuedDate: Optional[date] = None
    CertificationNumber: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeCertificationRead(EmployeeCertificationBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Skill Master Schemas (PascalCase model) ===
# =====================================================

class SkillMasterBase(BaseModel):
    SkillId: str = Field(..., example="SK-001")
    SkillName: str = Field(..., example="Python")
    SkillLevel: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class SkillMasterCreate(BaseModel):
    SkillName: str = Field(..., example="Python")
    SkillLevel: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"

class SkillMasterUpdate(BaseModel):
    SkillName: Optional[str] = None
    SkillLevel: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class SkillMasterRead(SkillMasterBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Task Type Master Schemas (PascalCase model) ===
# =====================================================

class TaskTypeMasterBase(BaseModel):
    TaskTypeId: str = Field(..., example="TT-001")
    TaskTypeName: str = Field(..., example="Development")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class TaskTypeMasterCreate(BaseModel):
    TaskTypeName: str = Field(..., example="Development")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"

class TaskTypeMasterUpdate(BaseModel):
    TaskTypeName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class TaskTypeMasterRead(TaskTypeMasterBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Task Schemas (Based on snake_case model) ===
# =====================================================

class TaskBase(BaseModel):
    # Mapping to Task model: task_id, deliverable_id, task_type_id, etc.
    task_id: str = Field(..., example="TASK-001")
    deliverable_id: str = Field(..., example="DEL-001")
    task_type_id: str = Field(..., example="TT-001")
    task_name: str = Field(..., example="Develop API Endpoint")
    task_description: Optional[str] = None
    assigne_id: Optional[str] = Field(None, example="EMP-002") # Mapped to assigne_id
    reviewer_id: Optional[str] = Field(None, example="EMP-003")
    priority: Optional[str] = Field(None, example="High")
    estimated_effort_in_hours: Optional[float] = None
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    entitystatus: Optional[str] = "Active"
    createdat: datetime = Field(default_factory=utcnow)
    updatedat: datetime = Field(default_factory=utcnow)
    createdby: Optional[str] = Field(None, example="USR-001")

class TaskCreate(BaseModel):
    deliverable_id: str = Field(..., example="DEL-001")
    task_type_id: str = Field(..., example="TT-001")
    task_name: str = Field(..., example="Develop API Endpoint")
    task_description: Optional[str] = None
    assigne_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    priority: Optional[str] = None
    estimated_effort_in_hours: Optional[float] = None
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    assigne_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    priority: Optional[str] = None
    estimated_effort_in_hours: Optional[float] = None
    plan_start_date: Optional[datetime] = None
    plan_end_date: Optional[datetime] = None
    entitystatus: Optional[str] = None
    updatedat: datetime = Field(default_factory=utcnow)


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Task Skill Requirement Schemas (PascalCase model) ===
# =====================================================

class TaskSkillRequirementBase(BaseModel):
    TaskSkillRequirementId: str = Field(..., example="TSR-001")
    TaskId: str = Field(..., example="TASK-001") # FK: task.task_id (Using TaskId for consistency)
    SkillId: str = Field(..., example="SK-001")
    Importance: Optional[str] = Field(None, example="High")


class TaskSkillRequirementCreate(BaseModel):
    TaskId: str = Field(..., example="TASK-001")
    SkillId: str = Field(..., example="SK-001")
    Importance: Optional[str] = None

class TaskSkillRequirementUpdate(BaseModel):
    SkillId: Optional[str] = None
    Importance: Optional[str] = None


class TaskSkillRequirementRead(TaskSkillRequirementBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Feedback Category Master Schemas (PascalCase model) ===
# =====================================================

class FeedbackCategoryMasterBase(BaseModel):
    FeedbackCategoryId: str = Field(..., example="FC-001")
    CategoryName: str = Field(..., example="Code Quality")


class FeedbackCategoryMasterCreate(BaseModel):
    CategoryName: str = Field(..., example="Code Quality")

class FeedbackCategoryMasterUpdate(BaseModel):
    CategoryName: Optional[str] = None


class FeedbackCategoryMasterRead(FeedbackCategoryMasterBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Review Schemas (PascalCase model) ===
# =====================================================

class ReviewBase(BaseModel):
    ReviewId: str = Field(..., example="REV-001")
    TaskId: str = Field(..., example="TASK-001")
    ReviewerId: str = Field(..., example="EMP-003")
    Status: Optional[str] = Field("Under Review", example="Under Review") # Capitalized to match CheckConstraint
    VerdictDate: Optional[date] = None
    OverallComments: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class ReviewCreate(BaseModel):
    TaskId: str = Field(..., example="TASK-001")
    ReviewerId: str = Field(..., example="EMP-003")
    Status: Optional[str] = Field("Under Review", example="Under Review")
    VerdictDate: Optional[date] = None
    OverallComments: Optional[str] = None

class ReviewUpdate(BaseModel):
    Status: Optional[str] = None
    VerdictDate: Optional[date] = None
    OverallComments: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Review Discussion Thread Schemas (PascalCase model) ===
# =====================================================

class ReviewDiscussionThreadBase(BaseModel):
    DiscussionId: str = Field(..., example="DISC-001")
    ReviewId: str = Field(..., example="REV-001")
    CommenterId: str = Field(..., example="EMP-001")
    CommentRole: Optional[str] = Field("Reviewer", example="Reviewer")
    RemarksText: Optional[str] = None
    CommentDate: Optional[date] = None
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class ReviewDiscussionThreadCreate(BaseModel):
    ReviewId: str = Field(..., example="REV-001")
    CommenterId: str = Field(..., example="EMP-001")
    CommentRole: Optional[str] = Field("Reviewer", example="Reviewer")
    RemarksText: Optional[str] = None
    CommentDate: Optional[date] = None

class ReviewDiscussionThreadUpdate(BaseModel):
    CommentRole: Optional[str] = None
    RemarksText: Optional[str] = None
    CommentDate: Optional[date] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class ReviewDiscussionThreadRead(ReviewDiscussionThreadBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Review Discussion Comment Schemas (PascalCase model) ===
# =====================================================

class ReviewDiscussionCommentBase(BaseModel):
    CommentId: str = Field(..., example="CMT-001")
    DiscussionId: str = Field(..., example="DISC-001")
    Comment: str = Field(..., example="Please fix variable naming convention.")


class ReviewDiscussionCommentCreate(BaseModel):
    DiscussionId: str = Field(..., example="DISC-001")
    Comment: str = Field(..., example="Please fix variable naming convention.")

class ReviewDiscussionCommentUpdate(BaseModel):
    Comment: Optional[str] = None


class ReviewDiscussionCommentRead(ReviewDiscussionCommentBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Audit Log Schemas (Based on snake_case model) ===
# NOTE: Audit logs are typically only created and read, not updated.
# =====================================================

class AuditLogBase(BaseModel):
    # Mapping to AuditLog model: audit_id, entity_type, entity_id, etc.
    audit_id: str = Field(..., example="AUD-001")
    entity_type: str = Field(..., example="Task")
    entity_id: str = Field(..., example="TASK-001")
    action: str = Field(..., example="Update")
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: Optional[str] = Field(None, example="EMP-002")
    createdat: datetime = Field(default_factory=utcnow)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# === Daily Status Schemas (PascalCase model) ===
# =====================================================

class DailyStatusBase(BaseModel):
    DailyStatusId: str = Field(..., example="DS-001")
    TaskId: str = Field(..., example="TASK-001")
    EmployeeId: Optional[str] = Field(None, example="EMP-001")
    WorkDate: date
    HoursSpent: Optional[float] = None
    Progress: Optional[float] = None
    Remarks: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=utcnow)
    UpdatedAt: datetime = Field(default_factory=utcnow)


class DailyStatusCreate(BaseModel):
    TaskId: str = Field(..., example="TASK-001")
    EmployeeId: Optional[str] = None
    WorkDate: date
    HoursSpent: Optional[float] = None
    Progress: Optional[float] = None
    Remarks: Optional[str] = None

class DailyStatusUpdate(BaseModel):
    HoursSpent: Optional[float] = None
    Progress: Optional[float] = None
    Remarks: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class DailyStatusRead(DailyStatusBase