<<<<<<< HEAD
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
=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    CreatedAt: datetime
    UpdatedAt: datetime

    class Config:
        orm_mode = True

<<<<<<< HEAD

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

=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class EmployeeCreate(EmployeeBase):
    pass

<<<<<<< HEAD
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
=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    AssignedToId: Optional[str] = None
    ReviewerId: Optional[str] = None
    Priority: Optional[str] = None
    PlannedStartDate: Optional[date] = None
<<<<<<< HEAD
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
=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class TaskSkillRequirementBase(BaseModel):
    TaskSkillRequirementId: str = Field(..., example="TSR-001")
    TaskId: str = Field(..., example="TASK-001")
    SkillId: str = Field(..., example="SK-001")
<<<<<<< HEAD
    Importance: Optional[str] = Field(None, example="High")

=======
    Importance: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class TaskSkillRequirementCreate(TaskSkillRequirementBase):
    pass

<<<<<<< HEAD
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

=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class FeedbackCategoryMasterCreate(FeedbackCategoryMasterBase):
    pass

<<<<<<< HEAD
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

=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class ReviewCreate(ReviewBase):
    pass

<<<<<<< HEAD
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

=======
class ReviewRead(ReviewBase):
    pass

class ReviewDiscussionThreadBase(BaseModel):
    ThreadId: str = Field(..., example="TH-001")
    ReviewId: str = Field(..., example="REV-001")
    Title: str = Field(..., example="Comments on integration")

    model_config = ConfigDict(from_attributes=True)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class ReviewDiscussionThreadCreate(ReviewDiscussionThreadBase):
    pass

<<<<<<< HEAD
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

=======
class ReviewDiscussionThreadRead(ReviewDiscussionThreadBase):
    pass

class ReviewDiscussionCommentBase(BaseModel):
    CommentId: str = Field(..., example="CMT-001")
    ThreadId: str = Field(..., example="TH-001")
    Comment: str = Field(..., example="Please fix this")

    model_config = ConfigDict(from_attributes=True)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class ReviewDiscussionCommentCreate(ReviewDiscussionCommentBase):
    pass

<<<<<<< HEAD
# ADDED ReviewDiscussionCommentUpdate
class ReviewDiscussionCommentUpdate(BaseModel):
    Comment: Optional[str] = None

=======
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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class ReviewDiscussionCommentRead(ReviewDiscussionCommentBase):
    class Config:
        orm_mode = True


<<<<<<< HEAD
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

=======
class AuditLogBase(BaseModel):
    Action: str = Field(..., example="CREATE")
    EntityName: str = Field(..., example="Deliverable")
    EntityId: str = Field(..., example="DEL-001")
    ChangedById: str = Field(..., example="USR-001")
    ChangeTimestamp: Optional[datetime] = None
    ChangeDetails: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef

class AuditLogCreate(AuditLogBase):
    pass

<<<<<<< HEAD

class AuditLogRead(AuditLogBase):
=======
class AuditLogRead(AuditLogBase):
    AuditLogId: str
    CreatedAt: datetime

>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
    class Config:
        orm_mode = True


<<<<<<< HEAD
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
=======


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
>>>>>>> da84f6c29baf1e41d41f4bbd83db02afe97cd3ef
