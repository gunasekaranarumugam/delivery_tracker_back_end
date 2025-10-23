from pydantic import BaseModel, Field, ConfigDict, constr, condecimal, validator
from typing import Optional, List, Literal
from datetime import date, datetime

# ------------------- User Schemas -------------------

class UserBase(BaseModel):
    UserId: str = Field(..., example="USR-123")
    fullName: Optional[str] = Field(None, example="John Doe")
    userName: str = Field(..., example="johndoe")
    emailID: Optional[str] = None
    FirstName: Optional[str] = None
    lastName: Optional[str] = None
    BUId: Optional[str] = None
    RoleId: Optional[str] = None
    #Role: Optional[str] = None  # We will populate this from property

    model_config = ConfigDict(from_attributes=True)

class UserRead(BaseModel):
    UserId: str
    userName: str
    fullName: Optional[str]
    emailID: Optional[str]
    BUId: str
    RoleId: Optional[str]
    #Role: Optional[str] = None  # We will populate this from property
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        # Create instance normally
        user = super().from_orm(obj)
        # Override Role field with role_name property
        user.Role = obj.role_name
        return user



from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str



class UserLoginResponse(BaseModel):
    userName: str
    BUId: str
    Role: str
    emailID: str
    FirstName: str
    lastName: str
    fullName: str
    authToken: str
    UserId: str

class UserLoginRequest(BaseModel):
    userName: str
    password: str

#class UserLoginResponse(UserBase):
#    authToken: str

class UserRegister(BaseModel):
    userName: str
    password: str
    BUId: str
    #RoleId: str
    emailID: Optional[str]
    FirstName: Optional[str]
    lastName: Optional[str]
    EmployeeId: str  # ✅ Add this
    Role: str = Field(None, example="PLEASE ENTER ROLE NAME CAPS LIKE THIS : (PROJECT MANAGER, BU HEAD, DEVELOPER, TEAM MEMBER, DELIVERY MANAGER, REVIEWER, ADMIN)")

# ------------------- Business Unit -------------------

class BusinessUnitBase(BaseModel):
    BUId: str = Field(..., example="BU-001")
    BUName: str = Field(..., example="Analytics BU")
    Description: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class BusinessUnitCreate(BusinessUnitBase):
    pass

class BusinessUnitRead(BusinessUnitBase):
    pass

# ------------------- Deliverable Schemas -------------------

class DeliverableCreate(BaseModel):
    DeliverableId: str
    ProjectId: str
    Title: str
    BUId: str
    Description: Optional[str] = None
    Priority: str
    PlannedStartDate: date
    PlannedEndDate: date
    ProjectManagerId: Optional[str]
    EntityStatus: str = "Active"
    ProjectManager: Optional[str]
    CreatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DeliverableRead(BaseModel):
    DeliverableId: str
    PlannedStartDate: Optional[date]
    PlannedEndDate: Optional[date]
    #Status: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# ------------------- Project Schemas -------------------

class ProjectBase(BaseModel):
    ProjectId: str = Field(..., example="PRJ-001")
    BUId: str = Field(..., example="BU-001")
    ProjectName: str = Field(..., example="Project A")
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    DeliveryManagerId: Optional[str] = Field(None, example="USR-123")
    DeliveryManager: Optional[str] = Field(None, example="John Doe")
    CreatedById: Optional[str] = None
    CreatedBy: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EmployeeBase(BaseModel):
    EmployeeId: str = Field(..., example="EMP-001")
    FullName: str = Field(..., example="Alice Dev")
    Email: Optional[str] = Field(None, example="alice@example.com")
    BUId: Optional[str] = None
    HolidayCalendarId: Optional[str] = None
    Status: Optional[str] = "Active"

    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeRead(EmployeeBase):
    pass

class ProjectCreate(BaseModel):
    ProjectId: str
    BUId: str
    ProjectName: str
    PlannedStartDate: Optional[date]
    PlannedEndDate: Optional[date]
    DeliveryManager: Optional[str]  # Can be UserId or userName

class ProjectRead(BaseModel):
    ProjectId: str
    ProjectName: str
    BUId: str
    PlannedStartDate: Optional[date]
    PlannedEndDate: Optional[date]
    DeliveryManager: Optional[EmployeeRead]
    CreatedBy: Optional[UserRead]
    deliverables: Optional[List[DeliverableRead]] = []
    EntityStatus: str
    CreatedAt: datetime

    model_config = ConfigDict(from_attributes=True)

# ------------------- Employee Schemas -------------------

class MilestoneBase(BaseModel):
    ProjectId: constr(max_length=50)
    Title: Optional[constr(max_length=150)] = None  # Make optional
    Description: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None

class MilestoneCreate(MilestoneBase):
    MilestoneId: constr(max_length=50)

class MilestoneRead(MilestoneBase):
    MilestoneId: str
    CreatedAt: Optional[datetime] = None
    UpdatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True

class DailyStatusBase(BaseModel):
    DeliverableId: constr(max_length=50)
    EmployeeId: Optional[constr(max_length=50)] = None
    WorkDate: date
    HoursSpent: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    Progress: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    Comment: Optional[str] = None

    @validator('HoursSpent')
    def hours_spent_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('HoursSpent must be >= 0')
        return v

    @validator('Progress')
    def progress_range(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Progress must be between 0 and 100')
        return v

class DailyStatusCreate(DailyStatusBase):
    DailyStatusId: constr(max_length=50)

class DailyStatusRead(DailyStatusBase):
    DailyStatusId: str
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True

class IssueBase(BaseModel):
    DeliverableId: constr(max_length=50)
    Title: constr(max_length=150)
    Description: Optional[str] = None
    ActionOwnerId: Optional[constr(max_length=50)] = None
    Priority: Optional[str] = None

class IssueCreate(IssueBase):
    IssueId: constr(max_length=50)

class IssueRead(IssueBase):
    IssueId: str
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True

class IssueActivityBase(BaseModel):
    IssueId: constr(max_length=50)
    EmployeeId: Optional[constr(max_length=50)] = None
    ActivityDate: Optional[datetime] = None
    Status: Optional[str] = None  # Could add Enum for validation
    Comment: Optional[str] = None

    @validator('Status')
    def status_check(cls, v):
        valid_status = {'Open', 'InProgress', 'Resolved', 'Closed'}
        if v is not None and v not in valid_status:
            raise ValueError(f'Status must be one of {valid_status}')
        return v

class IssueActivityCreate(IssueActivityBase):
    IssueActivityId: constr(max_length=50)

class IssueActivityRead(IssueActivityBase):
    IssueActivityId: str
    CreatedAt: datetime

    class Config:
        orm_mode = True

# DeliveryRating schemas
class DeliveryRatingBase(BaseModel):
    DeliverableId: str
    AttributeId: str
    RatedForId: str
    RatedById: str
    Score: condecimal(max_digits=4, decimal_places=2, ge=0, le=5)
    Comment: Optional[str] = None

class DeliveryRatingCreate(DeliveryRatingBase):
    pass

class DeliveryRatingUpdate(BaseModel):
    Score: Optional[condecimal(max_digits=4, decimal_places=2, ge=0, le=5)] = None
    Comment: Optional[str] = None
    Status: Optional[str] = None

class DeliveryRatingOut(DeliveryRatingBase):
    RatingId: str
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True

# EmployeeCapacity schemas
class EmployeeCapacityBase(BaseModel):
    EmployeeId: str
    BUId: str
    CapacityPerDayHours: condecimal(max_digits=4, decimal_places=1, gt=0)
    Location: Optional[str] = None

class EmployeeCapacityCreate(EmployeeCapacityBase):
    pass

class EmployeeCapacityUpdate(BaseModel):
    CapacityPerDayHours: Optional[condecimal(max_digits=4, decimal_places=1, gt=0)] = None
    Location: Optional[str] = None

class EmployeeCapacityOut(EmployeeCapacityBase):
    EmployeeCapacityId: str
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True

# EmployeeLeave schemas
class EmployeeLeaveBase(BaseModel):
    EmployeeId: str
    LeaveDate: date
    LeaveType: Optional[str] = None
    Reason: Optional[str] = None
    ApprovedById: Optional[str] = None
    Status: Optional[Literal['Pending', 'Approved', 'Rejected']] = None

class EmployeeLeaveCreate(EmployeeLeaveBase):
    pass

class EmployeeLeaveUpdate(BaseModel):
    LeaveType: Optional[str] = None
    Reason: Optional[str] = None
    ApprovedById: Optional[str] = None
    Status: Optional[Literal['Pending', 'Approved', 'Rejected']] = None

class EmployeeLeaveOut(EmployeeLeaveBase):
    LeaveId: str
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True

# ---------------- RatingAttributeMaster Schemas ----------------

class RatingAttributeMasterBase(BaseModel):
    AttributeName: str
    Description: Optional[str] = None
    Weight: Optional[condecimal(max_digits=5, decimal_places=2)] = 1.0

class RatingAttributeMasterCreate(RatingAttributeMasterBase):
    pass

class RatingAttributeMasterUpdate(RatingAttributeMasterBase):
    pass

class RatingAttributeMasterInDBBase(RatingAttributeMasterBase):
    AttributeId: str
    CreatedAt: Optional[datetime]
    UpdatedAt: Optional[datetime]

    class Config:
        orm_mode = True

class RatingAttributeMaster(RatingAttributeMasterInDBBase):
    pass

class EmployeeBase(BaseModel):
    EmployeeId: str = Field(..., example="EMP-001")
    FullName: str = Field(..., example="Alice Dev")
    Email: Optional[str] = Field(None, example="alice@example.com")
    BUId: Optional[str] = None
    HolidayCalendarId: Optional[str] = None
    Status: Optional[str] = "Active"

    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeRead(EmployeeBase):
    pass

# ------------------- Deliverable Assignment -------------------

# ------------------- Holiday Calendar -------------------

class HolidayCalendarBase(BaseModel):
    HolidayId: str = Field(..., example="HOL-001")
    HolidayName: str = Field(..., example="New Year")
    HolidayDate: date

    model_config = ConfigDict(from_attributes=True)

class HolidayCalendarCreate(HolidayCalendarBase):
    pass

class HolidayCalendarRead(HolidayCalendarBase):
    pass

# ------------------- Role Master -------------------

class RoleMasterBase(BaseModel):
    RoleId: str = Field(..., example="ROLE-001")
    RoleName: str = Field(..., example="Developer")

    model_config = ConfigDict(from_attributes=True)

class RoleMasterCreate(RoleMasterBase):
    pass

class RoleMasterRead(RoleMasterBase):
    pass

# ------------------- Task Schemas -------------------

class TaskBase(BaseModel):
    TaskId: str = Field(..., example="TASK-001")
    TaskTypeId: Optional[str] = None   # <-- make optional here
    DeliverableId: str = Field(..., example="DEL-001")
    Title: str = Field(..., example="Build API")
    AssignedToId: Optional[str] = None
    ReviewerId: Optional[str] = None
    Priority: Optional[str] = None
    PlannedStartDate: Optional[date] = None
    PlannedEndDate: Optional[date] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    pass

# ------------------- Employee Role -------------------
"""
class EmployeeRoleBase(BaseModel):
    EmployeeRoleId: str = Field(..., example="ER-001")
    EmployeeId: str = Field(..., example="EMP-001")
    RoleId: str = Field(..., example="ROLE-001")

    model_config = ConfigDict(from_attributes=True)

class EmployeeRoleCreate(EmployeeRoleBase):
    pass

class EmployeeRoleRead(EmployeeRoleBase):
    pass
"""

# ------------------- Task Type Master -------------------

class TaskTypeMasterBase(BaseModel):
    TaskTypeId: str = Field(..., example="TT-001")
    TaskTypeName: str = Field(..., example="Development")

    model_config = ConfigDict(from_attributes=True)

class TaskTypeMasterCreate(TaskTypeMasterBase):
    pass

class TaskTypeMasterRead(TaskTypeMasterBase):
    pass

# ------------------- Task Skill Requirement -------------------

class TaskSkillRequirementBase(BaseModel):
    TaskSkillRequirementId: str = Field(..., example="TSR-001")
    TaskId: str = Field(..., example="TASK-001")
    SkillId: str = Field(..., example="SK-001")
    Importance: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TaskSkillRequirementCreate(TaskSkillRequirementBase):
    pass

class TaskSkillRequirementRead(TaskSkillRequirementBase):
    pass

# ------------------- Skills -------------------

class SkillMasterBase(BaseModel):
    SkillId: str = Field(..., example="SK-001")
    SkillName: str = Field(..., example="Python")
    SkillLevel: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SkillMasterCreate(SkillMasterBase):
    pass

class SkillMasterRead(SkillMasterBase):
    pass

# ------------------- Certifications -------------------

class CertificationMasterBase(BaseModel):
    CertificationId: str = Field(..., example="CERT-001")
    CertificationName: str = Field(..., example="GCP Cert")

    model_config = ConfigDict(from_attributes=True)

class CertificationMasterCreate(CertificationMasterBase):
    pass

class CertificationMasterRead(CertificationMasterBase):
    pass

class EmployeeCertificationBase(BaseModel):
    EmployeeCertificationId: str = Field(..., example="EC-001")
    EmployeeId: str = Field(..., example="EMP-001")
    CertificationId: str = Field(..., example="CERT-001")

    model_config = ConfigDict(from_attributes=True)

class EmployeeCertificationCreate(EmployeeCertificationBase):
    pass

class EmployeeCertificationRead(EmployeeCertificationBase):
    pass

# ------------------- Feedback & Reviews -------------------

class FeedbackCategoryMasterBase(BaseModel):
    FeedbackCategoryId: str = Field(..., example="FC-001")
    CategoryName: str = Field(..., example="Must Have")

    model_config = ConfigDict(from_attributes=True)

class FeedbackCategoryMasterCreate(FeedbackCategoryMasterBase):
    pass

class FeedbackCategoryMasterRead(FeedbackCategoryMasterBase):
    pass

class ReviewBase(BaseModel):
    ReviewId: str = Field(..., example="REV-001")
    DeliverableId: str = Field(..., example="DEL-001")
    Summary: Optional[str] = None
    Status: Optional[str] = None
    EntityStatus: Optional[str] = "Active"
    CreatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(ReviewBase):
    pass

class ReviewRead(ReviewBase):
    pass

class ReviewDiscussionThreadBase(BaseModel):
    ThreadId: str = Field(..., example="TH-001")
    ReviewId: str = Field(..., example="REV-001")
    Title: str = Field(..., example="Comments on integration")

    model_config = ConfigDict(from_attributes=True)

class ReviewDiscussionThreadCreate(ReviewDiscussionThreadBase):
    pass

class ReviewDiscussionThreadRead(ReviewDiscussionThreadBase):
    pass

class ReviewDiscussionCommentBase(BaseModel):
    CommentId: str = Field(..., example="CMT-001")
    ThreadId: str = Field(..., example="TH-001")
    Comment: str = Field(..., example="Please fix this")

    model_config = ConfigDict(from_attributes=True)

class ReviewDiscussionCommentCreate(ReviewDiscussionCommentBase):
    pass

class ReviewDiscussionCommentRead(ReviewDiscussionCommentBase):
    pass

# ------------------- User Permissions -------------------

class UserPermissionBase(BaseModel):
    UserId: str
    Permission: str

    model_config = ConfigDict(from_attributes=True)

class UserPermissionCreate(UserPermissionBase):
    pass

class UserPermissionRead(UserPermissionBase):
    pass

# ------------------- Entity Status -------------------

class EntityStatusBase(BaseModel):
    StatusId: str
    StatusName: str

    model_config = ConfigDict(from_attributes=True)

class EntityStatusCreate(EntityStatusBase):
    pass

class EntityStatusRead(EntityStatusBase):
    pass


class ReviewDiscussionCommentBase(BaseModel):
    CommentId: str = Field(..., example="CMT-001")
    ThreadId: str = Field(..., example="TH-001")
    Comment: str = Field(..., example="Please fix this")
    CreatedById: Optional[str] = None
    CreatedAt: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReviewDiscussionCommentCreate(ReviewDiscussionCommentBase):
    pass

class ReviewDiscussionCommentRead(ReviewDiscussionCommentBase):
    class Config:
        orm_mode = True


class AuditLogBase(BaseModel):
    Action: str = Field(..., example="CREATE")
    EntityName: str = Field(..., example="Deliverable")
    EntityId: str = Field(..., example="DEL-001")
    ChangedById: str = Field(..., example="USR-001")
    ChangeTimestamp: Optional[datetime] = None
    ChangeDetails: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogRead(AuditLogBase):
    AuditLogId: str
    CreatedAt: datetime

    class Config:
        orm_mode = True




# ------------------- Final update_forward_refs calls -------------------

UserLoginResponse.update_forward_refs()
UserRead.update_forward_refs()
ProjectRead.update_forward_refs()
DeliverableRead.update_forward_refs()
DailyStatusRead.update_forward_refs()
IssueRead.update_forward_refs()
IssueActivityRead.update_forward_refs()
DeliveryRatingOut.update_forward_refs()
EmployeeCapacityOut.update_forward_refs()
EmployeeLeaveOut.update_forward_refs()
RatingAttributeMasterInDBBase.update_forward_refs()
EmployeeRead.update_forward_refs()
HolidayCalendarRead.update_forward_refs()
RoleMasterRead.update_forward_refs()
TaskRead.update_forward_refs()
TaskTypeMasterRead.update_forward_refs()
TaskSkillRequirementRead.update_forward_refs()
SkillMasterRead.update_forward_refs()
CertificationMasterRead.update_forward_refs()
EmployeeCertificationRead.update_forward_refs()
FeedbackCategoryMasterRead.update_forward_refs()
ReviewRead.update_forward_refs()
ReviewDiscussionThreadRead.update_forward_refs()
ReviewDiscussionCommentRead.update_forward_refs()
UserPermissionRead.update_forward_refs()
EntityStatusRead.update_forward_refs()
