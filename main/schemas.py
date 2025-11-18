from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


def now():
    return datetime.utcnow()


class EmployeeBase(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    password: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str = "Active"


class EmployeeViewBase(BaseModel):
    business_unit_id: Optional[str]
    business_unit_name: Optional[str]
    business_unit_head_id: Optional[str]
    business_unit_head_name: Optional[str]
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class EmployeeRegister(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    password: str
    business_unit_id: str


class EmployeeRead(EmployeeViewBase):
    model_config = {"from_attributes": True}


class EmployeeLoginResponse(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    auth_token: str


class EmployeeUpdate(BaseModel):
    business_unit_id: Optional[str] = None
    business_unit_name: Optional[str] = None
    business_unit_head_id: Optional[str] = None
    business_unit_head_name: Optional[str] = None
    employee_full_name: Optional[str] = None
    employee_email_address: Optional[str] = None
    business_unit_id: Optional[str] = None


class EmployeePatch(BaseModel):
    entity_status: Optional[str] = None


class BusinessUnitBase(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_description: str
    business_unit_head_id: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str = "Active"


class BusinessUnitViewBase(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_description: str
    business_unit_head_id: str
    business_unit_head_name: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class BusinessUnitCreate(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_description: str
    business_unit_head_id: str


class BusinessUnitUpdate(BaseModel):
    business_unit_name: Optional[str] = None
    business_unit_description: Optional[str] = None
    business_unit_head_id: Optional[str] = None
    business_unit_head_name: Optional[str] = None


class BusinessUnitPatch(BaseModel):
    entity_status: str


class BusinessUnitRead(BusinessUnitViewBase):
    class Config:
        from_attributes = True


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
    entity_status: str = "Active"


class ProjectViewBase(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_head_name: str
    project_id: str
    project_name: str
    project_description: str
    delivery_manager_id: str
    delivery_manager_name: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


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
    business_unit_name: Optional[str] = None
    delivery_manager_name: Optional[str] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None


class ProjectRead(ProjectViewBase):
    class Config:
        orm_mode = True


class ProjectPatch(ProjectBase):
    pass


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
    entity_status: str = "Active"


class DeliverableViewBase(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_head_name: str
    project_id: str
    project_name: str
    delivery_manager_id: str
    delivery_manager_name: str
    deliverable_id: str
    deliverable_name: str
    deliverable_description: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class DeliverableCreate(BaseModel):
    deliverable_id: str
    project_id: str
    deliverable_name: str
    deliverable_description: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_end_date: datetime
    planned_start_date: datetime


class DeliverableUpdate(BaseModel):
    project_id: Optional[str] = None
    deliverable_id: Optional[str] = None
    business_unit_name: Optional[str] = None
    business_unit_head_name: Optional[str] = None
    project_name: Optional[str] = None
    delivery_manager_id: Optional[str] = None
    deliverable_name: Optional[str] = None
    priority: Optional[str] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None


class DeliverableRead(DeliverableViewBase):
    class Config:
        orm_mode = True


class DeliverablePatch(DeliverableBase):
    pass


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
    effort_estimated_in_hours: str
    assignee_id: str
    reviewer_id: str


class TaskViewBase(BaseModel):
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_head_name: str
    project_id: str
    project_name: str
    delivery_manager_id: str
    delivery_manager_name: str
    deliverable_id: str
    deliverable_name: str
    task_id: str
    task_name: str
    task_description: str
    task_type_id: str
    task_type_name: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    effort_estimated_in_hours: str
    assignee_id: str
    assignee_name: str
    reviewer_id: str
    reviewer_name: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class TaskCreate(TaskBase):
    task_id: str
    deliverable_id: str
    task_name: str
    task_description: str
    task_type_id: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_end_date: datetime
    planned_start_date: datetime
    effort_estimated_in_hours: str
    assignee_id: str
    reviewer_id: str


class TaskUpdate(BaseModel):
    task_id: Optional[str]
    task_type_id: Optional[str]
    business_unit_id: Optional[str]
    business_unit_head_id: Optional[str]
    business_unit_head_name: Optional[str] = None
    project_name: Optional[str] = None
    delivery_manager_name: Optional[str] = None
    deliverable_name: Optional[str] = None
    task_type_name: Optional[str] = None
    task_description: Optional[str] = None
    assignee_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    assignee_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    priority: Optional[str] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None


class TaskRead(TaskViewBase):
    class Config:
        orm_mode = True


class TaskPatch(TaskBase):
    pass


class TaskTypeBase(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str = "Active"


class TaskTypeViewBase(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class TaskTypeCreate(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: str


class TaskTypeUpdate(BaseModel):
    task_type_Name: Optional[str] = None
    task_type_description: Optional[str] = None
    entity_status: Optional[str] = None


class TaskTypeRead(TaskTypeViewBase):
    class Config:
        orm_mode = True


class TaskTypePatch(TaskTypeBase):
    pass


class TaskStatusBase(BaseModel):
    task_status_id: str
    task_id: str
    action_date: datetime
    progress: str
    hours_spent: str
    remarks: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str = "Active"


class TaskStatusViewBase(BaseModel):
    task_status_id: str
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_head_name: str
    project_id: str
    project_name: str
    delivery_manager_id: str
    delivery_manager_name: str
    deliverable_id: str
    deliverable_name: str
    task_id: str
    task_name: str
    task_status_id: str
    action_date: datetime
    progress: str
    hours_spent: str
    remarks: str
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_by_name: str
    updated_by: str
    entity_status: str = "Active"

    class Config:
        from_attributes = True


class TaskStatusCreate(BaseModel):
    task_status_id: str
    task_id: str
    action_date: datetime
    progress: str
    hours_spent: str
    remarks: str


class TaskStatusUpdate(BaseModel):
    task_status_id: str
    task_id: str
    business_unit_id: str
    business_unit_head_id: str
    project_id: str
    business_unit_name: Optional[str] = None
    business_unit_head_name: Optional[str] = None
    project_name: Optional[str] = None
    delivery_manager_name: Optional[str] = None
    deliverable_name: Optional[str] = None
    task_name: Optional[str] = None
    action_date: Optional[datetime] = None
    progress: Optional[str] = None
    remarks: Optional[str] = None


class TaskStatusRead(TaskStatusViewBase):
    class Config:
        orm_mode = True


class TaskStatusPatch(TaskStatusBase):
    pass


class IssueBase(BaseModel):
    issue_id: str
    task_id: str
    issue_title: str
    issue_description: str
    action_owner_id: str
    priority: str
    status: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str = "Active"


class IssueViewBase(BaseModel):
    issue_id: str
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_head_name: str
    project_id: str
    project_name: str
    delivery_manager_id: str
    delivery_manager_name: str
    deliverable_id: str
    deliverable_name: str
    task_id: str
    task_name: str
    issue_id: str
    issue_title: str
    issue_description: str
    issue_priority: str
    issue_status: str
    action_owner_id: str
    action_owner_name: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class IssueCreate(BaseModel):
    issue_id: str
    task_id: str
    issue_title: str
    issue_description: str
    action_owner_id: str
    issue_priority: str
    issue_status: str


class IssueUpdate(BaseModel):
    business_unit_id: Optional[str]
    business_unit_name: Optional[str] = None
    project_id: Optional[str]
    project_name: Optional[str] = None
    deliverable_id: Optional[str]
    deliverable_name: Optional[str] = None
    task_id: Optional[str]
    task_name: Optional[str] = None
    issue_id: Optional[str]
    issue_title: Optional[str] = None
    issue_description: Optional[str] = None
    action_owner_id: Optional[str]
    action_owner_name: Optional[str] = None
    issue_priority: Optional[str] = None
    issue_status: Optional[str] = None


class IssueRead(IssueViewBase):
    class Config:
        orm_mode = True


class IssuePatch(IssueBase):
    pass


class IssueActivityBase(BaseModel):
    issue_activity_id: str
    issue_id: str
    comment_by: str
    comment_at: datetime = Field(default_factory=now)
    comment: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str = "Active"


class IssueActivityViewBase(BaseModel):
    issue_activity_id: str
    business_unit_id: str
    business_unit_name: str
    business_unit_head_id: str
    business_unit_head_name: str
    project_id: str
    project_name: str
    delivery_manager_id: str
    delivery_manager_name: str
    deliverable_id: str
    deliverable_name: str
    task_id: str
    task_name: str
    issue_id: str
    issue_activity_id: str
    comment_by: str
    comment_by_name: str
    comment_at: datetime = Field(default_factory=now)
    comment: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    updated_by_name: str
    entity_status: str = "Active"


class IssueActivityCreate(BaseModel):
    issue_activity_id: str
    issue_id: str
    comment_by: str
    comment: str


class IssueActivityUpdate(BaseModel):
    comment: Optional[str] = None
    entity_status: Optional[str] = None


class IssueActivityRead(IssueActivityViewBase):
    class Config:
        from_attributes = True


class IssueActivityPatch(IssueActivityBase):
    pass


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
