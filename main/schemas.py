# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# =====================================================
# === Utility ===
# =====================================================
def now():
    return datetime.utcnow()


# =====================================================
# === Employee Schemas ===
# =====================================================
class EmployeeBase(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    password: str
    business_unit_id: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class EmployeeRegister(BaseModel):
    employee_id : str
    employee_full_name: str
    employee_email_address: str
    password: str
    business_unit_id: str

class EmployeeLogin(BaseModel):
    employee_email_address: str
    password: str

class EmployeeRead(EmployeeBase):
    class Config:
        orm_mode = True

class EmployeeLoginResponse(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    auth_token: str

class EmployeePatch(BaseModel):
    employee_full_name: Optional[str] = None
    employee_email_address: Optional[str] = None
    password: Optional[str] = None
    business_unit_id: Optional[str] = None
    updated_by: str  # usually required to track who updated
    entity_status: Optional[str] = None


# =====================================================
# === Business Unit Schemas ===
# =====================================================
class BusinessUnitBase(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_description: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class BusinessUnitCreate(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_description: str

class BusinessUnitUpdate(BaseModel):
    business_unit_name: Optional[str] = None
    business_unit_head_id: Optional[str] = None
    business_unit_description: Optional[str] = None
    entity_status: Optional[str] = None

class BusinessUnitPatch(BaseModel):
    business_unit_name: Optional[str] = None
    business_unit_head_id: Optional[str] = None
    business_unit_description: Optional[str] = None
    entity_status: Optional[str] = None


class BusinessUnitRead(BusinessUnitBase):
    class Config:
        orm_mode = True


# =====================================================
# === Project Schemas ===
# =====================================================
class ProjectBase(BaseModel):
    project_id: str
    business_unit_id: str
    project_name: str
    project_description: str
    delivery_manager_id: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class ProjectCreate(BaseModel):
    project_id: str
    business_unit_id: str
    project_name: str
    project_description: str
    delivery_manager_id: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    delivery_manager_id: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    entity_status: Optional[str] = None

class ProjectPatch(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    delivery_manager_id: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    entity_status: Optional[str] = None


class ProjectRead(ProjectBase):
    class Config:
        orm_mode = True


# =====================================================
# === Deliverable Schemas ===
# =====================================================
class DeliverableBase(BaseModel):
    deliverable_id: str
    project_id: str
    deliverable_name: str
    deliverable_description: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class DeliverableCreate(BaseModel):
    deliverable_id: str
    project_id: str
    deliverable_name: str
    deliverable_description: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime


class DeliverableUpdate(BaseModel):
    deliverable_id: Optional[str]
    project_id: Optional[str]
    deliverable_name: Optional[str]
    deliverable_description: Optional[str]
    baseline_start_date: Optional[datetime]
    baseline_end_date: Optional[datetime]
    planned_start_date: Optional[datetime]
    planned_end_date: Optional[datetime]
    priority: Optional[str]

    class Config:
        orm_mode = True


class DeliverablePatch(BaseModel):
    deliverable_name: Optional[str] = None
    deliverable_description: Optional[str] = None
    priority: Optional[str]
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    entity_status: Optional[str] = None


class DeliverableRead(DeliverableBase):
    class Config:
        orm_mode = True


# =====================================================
# === Task Schemas ===
# =====================================================
class TaskBase(BaseModel):
    task_id: str
    deliverable_id: str
    task_name: str
    task_description: str
    task_type_id: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    effort_estimated_in_hours: float
    assignee_id: str
    reviewer_id: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class TaskCreate(BaseModel):
    task_id: str
    deliverable_id: str
    task_name: str
    task_description: str
    task_type_id: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    effort_estimated_in_hours: float
    assignee_id: Optional[str] = None
    reviewer_id: Optional[str] = None

class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    task_type_id: Optional[str] = None
    priority: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    effort_estimated_in_hours: Optional[float] = None
    assignee_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    entity_status: Optional[str] = None

class TaskPatch(BaseModel):
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    task_type_id: Optional[str] = None
    priority: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    effort_estimated_in_hours: Optional[float] = None
    assignee_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    entity_status: Optional[str] = None


class TaskRead(TaskBase):
    class Config:
        orm_mode = True


# =====================================================
# === Task Type Master Schemas ===
# =====================================================
class TaskTypeMasterBase(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class TaskTypeMasterCreate(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: Optional[str] = None

class TaskTypeMasterUpdate(BaseModel):
    task_type_Name: Optional[str] = None
    task_type_description: Optional[str] = None
    entity_status: Optional[str] = None

class TaskTypeMasterPatch(BaseModel):
    task_type_Name: Optional[str] = None
    task_type_description: Optional[str] = None
    entity_status: Optional[str] = None


class TaskTypeMasterRead(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    entity_status: Optional[str] = None

    class Config:
        orm_mode = True


# =====================================================
# === Task Status Schemas ===
# =====================================================
class TaskStatusCreate(BaseModel):
    task_status_id: str
   
    progress: str
    hours_spent: str
    remarks: str

class TaskStatusUpdate(BaseModel):
    task_status_id: str
  
    progress: str
    hours_spent: str
    remarks: str

class TaskStatusRead(BaseModel):
    task_status_id: str
   
    progress: str
    hours_spent: str
    remarks: str

    class Config:
        orm_mode = True

class TaskStatusPatch(BaseModel):
    task_status_id: str
 
    progress: str
    hours_spent: str
    remarks: str



# =====================================================
# === Issue Schemas ===
# =====================================================
class IssueBase(BaseModel):
    issue_id: str
    task_id: str
    issue_title: str
    issue_description: Optional[str] = None
    action_owner_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)

class IssueCreate(BaseModel):
    issue_id: str
    task_id: str
    issue_title: str
    issue_description: Optional[str] = None
    action_owner_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class IssueUpdate(BaseModel):
    issue_id: Optional[str] = None
    issue_title: Optional[str] = None
    issue_description: Optional[str] = None
    action_owner_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class IssueRead(IssueBase):
    class Config:
        orm_mode = True

class IssuePatch(BaseModel):
    issue_id: Optional[str] = None
    issue_title: Optional[str] = None
    issue_description: Optional[str] = None
    action_owner_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


# =====================================================
# === Issue Activity Schemas ===
# =====================================================


class IssueActivityBase(BaseModel):
    issue_activity_id: str
    issueId: str
    comment_by: Optional[str] = None
    comment_at: Optional[datetime] = Field(default_factory=now)
    comment: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=now)
    updated_at: Optional[datetime] = Field(default_factory=now)
    updated_by: Optional[str] = None
    entity_status: Optional[str] = "Active"



class IssueActivityCreate(BaseModel):
    issue_activity_id: str
    issueId: str
    comment_by: Optional[str] = None
    comment: Optional[str] = None
  


class IssueActivityRead(IssueActivityBase):
    class Config:
        orm_mode = True


class IssueActivityPatch(BaseModel):
    issue_activity_id: Optional[str] = None
    issueId: Optional[str] = None
    comment_by: Optional[str] = None
    comment: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    entity_status: Optional[str] = None



# =====================================================
# === Audit Log Schemas ===
# =====================================================
class AuditLogBase(BaseModel):
    audit_id: str
    entity_type: str
    entity_id: str
    action: str
    action_date: datetime = Field(default_factory=now)
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None

class AuditLogCreate(BaseModel):
    entity_type: str
    entity_id: str
    action: str
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None

class AuditLogRead(AuditLogBase):
    class Config:
        orm_mode = True


class AuditLogPatch(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None

