# schemas.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# Utility default for timestamps
def now():
    return datetime.datetime.utcnow()

# =====================================================
# === Employee Schemas ===
# =====================================================

class EmployeeBase(BaseModel):
    employee_id: str = Field(..., example="EMP-001")
    employee_full_name: str = Field(..., example="John Doe")
    employee_email_address: str = Field(..., example="john.doe@example.com") 
    password: str = Field(..., example="Secure@123") 
    business_unit_id: str = Field(..., example="BU-001") 
    holiday_calendar_id: str = Field(..., example="CAL-001")
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class EmployeeRegister(BaseModel):
    employee_full_name: str = Field(..., example="John Doe")
    employee_email_address: str = Field(..., example="john.doe@example.com") 
    password: str = Field(..., example="Secure@123") 
    business_unit_id: str = Field(..., example="BU-001") 
    holiday_calendar_id: str = Field(..., example="CAL-001")

class EmployeeLogin(BaseModel):
    employee_email_address: str
    password: str

class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    business_unit_id: str
    holiday_calendar_id: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    entity_status: str
    
class EmployeeLoginResponse(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    auth_token: str

# =====================================================
# === Business Unit Schemas ===
# =====================================================

class BusinessUnitBase(BaseModel):
    business_unit_id: str = Field(..., example="BU-001")
    business_unit_name: str = Field(..., example="Analytics BU")
    business_unit_head_id: str = Field(..., example="EMP-001")
    business_unit_description: str = Field(..., example="Analytics BU")
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class BusinessUnitCreate(BaseModel):
    business_unit_id: str = Field(..., example="BU-001")
    business_unit_name: str = Field(..., example="Analytics BU")
    business_unit_head_id: str = Field(..., example="EMP-001")
    business_unit_description: str = Field(..., example="Analytics BU")
    
class BusinessUnitUpdate(BaseModel):
    business_unit_id: str = Field(..., example="BU-001")
    business_unit_name: str = Field(..., example="Analytics BU")
    business_unit_head_id: str = Field(..., example="EMP-001")
    business_unit_description: str = Field(..., example="Analytics BU")

class BusinessUnitRead(BusinessUnitBase):
    model_config = ConfigDict(from_attributes=True)
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_description: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    entity_status: str
    
# =====================================================
# === Project Schemas ===
# =====================================================

class ProjectBase(BaseModel):
    project_id: str = Field(..., example="PRJ-001")
    business_unit_id: str = Field(..., example="BU-001")
    project_name: str = Field(..., example="Project Alpha")
    project_description: str = Field(..., example="Project Alpha")
    delivery_manager_id: str = Field(..., example="EMP-002")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class ProjectCreate(BaseModel):
    business_unit_id: str = Field(..., example="BU-001")
    project_id: str = Field(..., example="PRJ-001")
    project_name: str = Field(..., example="Project Alpha")
    project_description: str = Field(..., example="Project Alpha")
    delivery_manager_id: str = Field(..., example="EMP-002")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)

class ProjectUpdate(BaseModel):
    business_unit_id: str = Field(..., example="BU-001")
    project_id: str = Field(..., example="PRJ-001")
    project_name: str = Field(..., example="Project Alpha")
    project_description: str = Field(..., example="Project Alpha")
    delivery_manager_id: str = Field(..., example="EMP-002")
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    entity_status: str = Field(..., example="Active")

class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    business_unit_id: str
    project_id: str
    project_name: str
    project_description: str
    delivery_manager_id: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    plan_start_date: datetime
    plan_end_date: datetime
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    entity_status: str

# =====================================================
# === Deliverable Schemas ===
# =====================================================

class DeliverableBase(BaseModel):
    deliverable_id: str = Field(..., example="DEL-001")
    project_id: str = Field(..., example="PRJ-001")
    deliverbale_name: str = Field(..., example="UI Module Delivery")
    deliverable_description: str = Field(..., example="UI Module Delivery")
    priority: str = Field(..., example="High")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class DeliverableCreate(BaseModel):
    deliverable_id: str = Field(..., example="DEL-001")
    project_id: str = Field(..., example="PRJ-001")
    deliverbale_name: str = Field(..., example="UI Module Delivery")
    deliverable_description: str = Field(..., example="UI Module Delivery")
    priority: str = Field(..., example="High")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)

class DeliverableUpdate(BaseModel):
    deliverable_id: str = Field(..., example="DEL-001")
    project_id: str = Field(..., example="PRJ-001")
    deliverbale_name: str = Field(..., example="UI Module Delivery")
    deliverable_description: str = Field(..., example="UI Module Delivery")
    priority: str = Field(..., example="High")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    entity_status: str = Field(..., example="Active")
    
class DeliverableRead(DeliverableBase):
    model_config = ConfigDict(from_attributes=True)
    project_id: str
    deliverable_id: str
    deliverbale_name: str
    deliverable_description: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    plan_start_date: datetime
    plan_end_date: datetime
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    entity_status: str

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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]

class MilestoneCreate(MilestoneBase):
    """Schema used for creating a new Milestone."""
    pass

class MilestoneUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class MilestoneRead(MilestoneBase):
    """Schema used for reading Milestone data (response model)."""
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Holiday Calendar Schemas ===
# =====================================================

class HolidayCalendarBase(BaseModel):
    HolidayCalendarId: str = Field(..., example="HC-001")
    CalendarName: Optional[str] = Field(None, example="India Public Holidays")
    Description: Optional[str] = Field(None, example="All official holidays for India region")
    EntityStatus: Optional[str] = Field("Active", example="Active")
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class HolidayCalendarCreate(HolidayCalendarBase):
    """Used for creating a new Holiday Calendar."""
    pass

class HolidayCalendarUpdate(BaseModel):
    CalendarName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class HolidayCalendarRead(HolidayCalendarBase):
    """Used for reading Holiday Calendar data (response model)."""
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Holiday Schemas ===
# =====================================================

class HolidayBase(BaseModel):
    HolidayId: str = Field(..., example="HOL-001")
    HolidayCalendarId: str = Field(..., example="HC-001")
    Date: date = Field(..., example="2025-01-26")
    HolidayName: str = Field(..., example="Republic Day")
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class HolidayCreate(HolidayBase):
    """Used for creating a new Holiday entry."""
    pass

class HolidayUpdate(BaseModel):
    Date: Optional[date] = None
    HolidayName: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class HolidayRead(HolidayBase):
    """Used for reading Holiday data (response model)."""
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Role Master Schemas ===
# =====================================================

class RoleMasterBase(BaseModel):
    RoleId: str = Field(..., example="ROLE-001")
    RoleName: str = Field(..., example="Developer")
    Description: Optional[str] = None
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class RoleMasterCreate(RoleMasterBase):
    pass

class RoleMasterUpdate(BaseModel):
    RoleName: Optional[str] = None
    Description: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class RoleMasterRead(RoleMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    FullName: Optional[str] = None
    Email: Optional[str] = None
    BUId: Optional[str] = None
    Status: Optional[str] = None
    HolidayCalendarId: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class EmployeeRoleCreate(EmployeeRoleBase):
    pass

class EmployeeRoleUpdate(BaseModel):
    RoleId: Optional[str] = None
    Active: Optional[bool] = None
    AssignedDate: Optional[date] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeRoleRead(EmployeeRoleBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class CertificationMasterCreate(CertificationMasterBase):
    pass

class CertificationMasterUpdate(BaseModel):
    CertificationName: Optional[str] = None
    SkillId: Optional[str] = None
    IssuingAuthority: Optional[str] = None
    ValidDurationDays: Optional[int] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class CertificationMasterRead(CertificationMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class EmployeeCertificationCreate(EmployeeCertificationBase):
    pass

class EmployeeCertificationUpdate(BaseModel):
    CertificationId: Optional[str] = None
    IssuedDate: Optional[date] = None
    CertificationNumber: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeCertificationRead(EmployeeCertificationBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Skill Master Schemas ===
# =====================================================

class SkillMasterBase(BaseModel):
    SkillId: str = Field(..., example="SK-001")
    SkillName: str = Field(..., example="Python")
    SkillLevel: Optional[str] = Field(None, example="Expert")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class SkillMasterCreate(SkillMasterBase):
    pass

class SkillMasterUpdate(BaseModel):
    SkillName: Optional[str] = None
    SkillLevel: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class SkillMasterRead(SkillMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Task Type Master Schemas ===
# =====================================================

class TaskTypeMasterBase(BaseModel):
    TaskTypeId: str = Field(..., example="TT-001")
    TaskTypeName: str = Field(..., example="Development")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class TaskTypeMasterCreate(TaskTypeMasterBase):
    pass

class TaskTypeMasterUpdate(BaseModel):
    TaskTypeName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class TaskTypeMasterRead(TaskTypeMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Task Schemas ===
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
    task_id: str = Field(..., example="TASK-001")
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
    task_id: str = Field(..., example="TASK-001")
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
# === Task Skill Requirement Schemas ===
# =====================================================

class TaskSkillRequirementBase(BaseModel):
    TaskSkillRequirementId: str = Field(..., example="TSR-001")
    TaskId: str = Field(..., example="TASK-001")
    SkillId: str = Field(..., example="SK-001")
    Importance: Optional[str] = Field(None, example="High")


class TaskSkillRequirementCreate(TaskSkillRequirementBase):
    pass

class TaskSkillRequirementUpdate(BaseModel):
    SkillId: Optional[str] = None
    Importance: Optional[str] = None


class TaskSkillRequirementRead(TaskSkillRequirementBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Feedback Category Master Schemas ===
# =====================================================

class FeedbackCategoryMasterBase(BaseModel):
    FeedbackCategoryId: str = Field(..., example="FC-001")
    CategoryName: str = Field(..., example="Code Quality")


class FeedbackCategoryMasterCreate(FeedbackCategoryMasterBase):
    pass

class FeedbackCategoryMasterUpdate(BaseModel):
    CategoryName: Optional[str] = None


class FeedbackCategoryMasterRead(FeedbackCategoryMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    Status: Optional[str] = None
    VerdictDate: Optional[date] = None
    OverallComments: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class ReviewDiscussionThreadCreate(ReviewDiscussionThreadBase):
    pass

class ReviewDiscussionThreadUpdate(BaseModel):
    CommentRole: Optional[str] = None
    RemarksText: Optional[str] = None
    CommentDate: Optional[date] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class ReviewDiscussionThreadRead(ReviewDiscussionThreadBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Review Discussion Comment Schemas ===
# =====================================================

class ReviewDiscussionCommentBase(BaseModel):
    CommentId: str = Field(..., example="CMT-001")
    DiscussionId: str = Field(..., example="DISC-001") # Corrected from ThreadId to DiscussionId per model
    Comment: str = Field(..., example="Please fix variable naming convention.")
    # Assuming CreatedAt/UpdatedAt are not in the model for this simple entity, otherwise add them here.


class ReviewDiscussionCommentCreate(ReviewDiscussionCommentBase):
    pass

class ReviewDiscussionCommentUpdate(BaseModel):
    Comment: Optional[str] = None


class ReviewDiscussionCommentRead(ReviewDiscussionCommentBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Audit Log Schemas ===
# =====================================================
# NOTE: Audit logs are typically only created and read, not updated.

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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class DailyStatusCreate(DailyStatusBase):
    pass

class DailyStatusUpdate(BaseModel):
    HoursSpent: Optional[float] = None
    Progress: Optional[float] = None
    Remarks: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class DailyStatusRead(DailyStatusBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    ActionOwnerId: Optional[str] = None
    Priority: Optional[str] = None
    Status: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class IssueRead(IssueBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class IssueActivityCreate(IssueActivityBase):
    pass


class IssueActivityRead(IssueActivityBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Rating Attribute Master Schemas ===
# =====================================================

class RatingAttributeMasterBase(BaseModel):
    AttributeId: str = Field(..., example="RA-001")
    AttributeName: str = Field(..., example="Code Quality")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class RatingAttributeMasterCreate(RatingAttributeMasterBase):
    pass

class RatingAttributeMasterUpdate(BaseModel):
    AttributeName: Optional[str] = None
    Description: Optional[str] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class RatingAttributeMasterRead(RatingAttributeMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


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
    UpdatedAt: datetime = Field(default_factory=utcnow)


class DeliveryRatingRead(DeliveryRatingBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX

# ADDED ALIAS DeliveryRatingOut to fix router import error (Keep for compatibility)
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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class EmployeeSkillCreate(EmployeeSkillBase):
    pass

class EmployeeSkillUpdate(BaseModel):
    SkillId: Optional[str] = None
    IsPrimary: Optional[bool] = None
    ExperienceYears: Optional[float] = None
    EntityStatus: Optional[str] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


class EmployeeSkillRead(EmployeeSkillBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX


# =====================================================
# === Employee Capacity Schemas ===
# =====================================================

class EmployeeCapacityBase(BaseModel):
    EmployeeCapacityId: str = Field(..., example="ECAP-001")
    EmployeeId: str = Field(..., example="EMP-001")
    BUId: str = Field(..., example="BU-001")
    CapacityHours: float = Field(..., example=8.0)
    CapaCityDate: Optional[date] = None
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class EmployeeCapacityCreate(EmployeeCapacityBase):
    pass


class EmployeeCapacityRead(EmployeeCapacityBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX

# ADDED ALIAS EmployeeCapacityOut to fix router import error (Keep for compatibility)
class EmployeeCapacityOut(EmployeeCapacityRead):
    pass

class EmployeeCapacityUpdate(BaseModel):
    """
    Schema for updating an existing Employee Capacity entry.
    All fields are Optional as updates typically only contain fields being changed.
    """
    EmployeeId: Optional[str] = Field(None, example="EMP-001")
    BUId: Optional[str] = Field(None, example="BU-001")
    CapacityHours: Optional[float] = Field(None, example=7.0)
    CapaCityDate: Optional[date] = None
    UpdatedAt: datetime = Field(default_factory=utcnow)


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
    CreatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]
    UpdatedAt: datetime = Field(default_factory=utcnow) # Removed Optional[]


class EmployeeLeaveCreate(EmployeeLeaveBase):
    pass


class EmployeeLeaveRead(EmployeeLeaveBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX

# ADDED EmployeeLeaveOut to fix router import error (Keep for compatibility)
class EmployeeLeaveOut(EmployeeLeaveRead):
    pass

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
    UpdatedAt: datetime = Field(default_factory=utcnow)
