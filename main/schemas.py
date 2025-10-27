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

class EmployeeLogin(EmployeeBase):
    employee_email_address: str
    password: str

class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    business_unit_id: str
    
class EmployeeLoginResponse(EmployeeBase):
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

# =====================================================
# === Task Schemas ===
# =====================================================

class TaskBase(BaseModel):
    task_id: str = Field(..., example="TASK-001")
    deliverable_id: str = Field(..., example="DEL-001")
    task_name: str = Field(..., example="Develop API Endpoint")
    task_description: str = Field(..., example="Develop API Endpoint")
    task_type_id: str = Field(..., example="TT-001")
    priority: str = Field(..., example="High")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    estimated_effort_in_hours: str = Field(..., example="4.5")
    assignee_id: str = Field(..., example="EMP-002")
    reviewer_id: str = Field(..., example="EMP-002")
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class TaskCreate(BaseModel):
    task_id: str = Field(..., example="TASK-001")
    deliverable_id: str = Field(..., example="DEL-001")
    task_name: str = Field(..., example="Develop API Endpoint")
    task_description: str = Field(..., example="Develop API Endpoint")
    task_type_id: str = Field(..., example="TT-001")
    priority: str = Field(..., example="High")
    baseline_start_date: datetime =  Field(..., example=now)
    baseline_end_date: datetime =  Field(..., example=now)
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    estimated_effort_in_hours: str = Field(..., example="4.5")
    assignee_id: str = Field(..., example="EMP-002")
    reviewer_id: str = Field(..., example="EMP-002")

class TaskUpdate(BaseModel):
    task_id: str = Field(..., example="TASK-001")
    deliverable_id: str = Field(..., example="DEL-001")
    task_name: str = Field(..., example="Develop API Endpoint")
    task_description: str = Field(..., example="Develop API Endpoint")
    task_type_id: str = Field(..., example="TT-001")
    priority: str = Field(..., example="High")
    plan_start_date: datetime =  Field(..., example=now)
    plan_end_date: datetime =  Field(..., example=now)
    estimated_effort_in_hours: str = Field(..., example="4.5")
    assignee_id: str = Field(..., example="EMP-002")
    reviewer_id: str = Field(..., example="EMP-002")
    entity_status: str = Field(..., example="Active")

class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    deliverable_id: str
    task_id: str
    task_name: str
    task_description: str
    task_type_id: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    plan_start_date: datetime
    plan_end_date: datetime
    estimated_effort_in_hours: str
    assignee_id: str
    reviewer_id: str
    
# =====================================================
# === Task Type Schemas ===
# =====================================================

class TaskTypeBase(BaseModel):
    task_type_id: str = Field(..., example="TT-001")
    task_type_name: str = Field(..., example="Development")
    task_type_description: str = Field(..., example="Development")
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class TaskTypeCreate(BaseModel):
    task_type_id: str = Field(..., example="TT-001")
    task_type_name: str = Field(..., example="Development")
    task_type_description: str = Field(..., example="Development")

class TaskTypeUpdate(BaseModel):
    task_type_id: str = Field(..., example="TT-001")
    task_type_name: str = Field(..., example="Development")
    task_type_description: str = Field(..., example="Development")
    entity_status: str = Field(..., example="Active")

class TaskTypeMasterRead(TaskTypeMasterBase):
    model_config = ConfigDict(from_attributes=True) # ✅ Pydantic V2 FIX
    task_type_id: str
    task_type_name: str
    task_type_description:str

class TaskTypeMasterCreate(TaskTypeMasterBase):
    pass

class TaskTypeMasterRead(TaskTypeMasterBase):
    pass

# =====================================================
# === Task Status Schemas ===
# =====================================================
   
class TaskStatusBase(BaseModel):
    task_status_id: str = Field(..., example="TS-001")
    task_id: str = Field(..., example="TASK-001")
    action_date: date
    hours_spent: str = Field(..., example="4.5")
    progress: str = Field(..., example="20%")
    remarks: str = Field(..., example="REMARKS-001")
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")

class TaskStatusCreate(BaseModel):
    task_status_id: str = Field(..., example="TS-001")
    task_id: str = Field(..., example="TASK-001")
    action_date: date
    hours_spent: str = Field(..., example="4.5")
    progress: str = Field(..., example="20%")
    remarks: str = Field(..., example="REMARKS-001")
    created_at: datetime = Field(default_factory=now)
    created_by: str = Field(..., example="EMP-001")

class DailyStatusUpdate(BaseModel):
    task_status_id: str = Field(..., example="TS-001")
    task_id: str = Field(..., example="TASK-001")
    action_date: date
    hours_spent: str = Field(..., example="4.5")
    progress: str = Field(..., example="20%")
    remarks: str = Field(..., example="REMARKS-001")
    updated_at: datetime = Field(default_factory=now)
    updated_by: str = Field(..., example="EMP-001")
    entity_status: str = Field(..., example="Active")

class DailyStatusRead(DailyStatusBase):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True) 

# =====================================================
# === Audit Log Schemas ===
# =====================================================

class AuditLogBase(BaseModel):
    audit_id: str = Field(..., example="AUD-001")
    entity_type: str = Field(..., example="Task")
    entity_id: str = Field(..., example="TASK-001")
    action: str = Field(..., example="Update")
    field_changed: str = Field(..., example="Task Name")
    old_value: str = Field(..., example="Task 1")
    new_value: str = Field(..., example="Task 1B")
    changed_at: datetime = Field(default_factory=now)
    changed_by: str = Field(..., example="EMP-001")

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)
