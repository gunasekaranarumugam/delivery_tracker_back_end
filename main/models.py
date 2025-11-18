from sqlalchemy import Column, Date, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

from .utils import now_utc


Base = declarative_base()


class Employee(Base):
    __tablename__ = "employee"
    employee_id = Column(String(10), primary_key=True, index=True)
    employee_full_name = Column(String(100))
    employee_email_address = Column(String(100))
    password = Column(String(100))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class EmployeeView(Base):
    __tablename__ = "vw_employee"
    employee_id = Column(String(10), primary_key=True, index=True)
    employee_full_name = Column(String(100))
    employee_email_address = Column(String(100))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class BusinessUnit(Base):
    __tablename__ = "business_unit"
    business_unit_id = Column(String(10), primary_key=True, index=True)
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_description = Column(String(4000))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class BusinessUnitView(Base):
    __tablename__ = "vw_business_unit"
    business_unit_id = Column(String(10), primary_key=True, index=True)
    business_unit_name = Column(String(100))
    business_unit_description = Column(String(4000))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class EmployeeBusinessUnit(Base):
    __tablename__ = "employee_business_unit"
    employee_id = Column(String(10), primary_key=True, index=True)
    business_unit_id = Column(String(10))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class EmployeeBusinessUnitView(Base):
    __tablename__ = "vw_employee_business_unit"
    business_unit_id = Column(String(10), primary_key=True, index=True)
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    employee_id = Column(String(10), primary_key=True, index=True)
    employee_full_name = Column(String(100))
    employee_email_address = Column(String(100))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class Project(Base):
    __tablename__ = "project"
    project_id = Column(String(10), primary_key=True, index=True)
    business_unit_id = Column(String(10))
    project_name = Column(String(100))
    project_description = Column(String(4000))
    delivery_manager_id = Column(String(10))
    baseline_start_date = Column(DateTime, default=now_utc())
    baseline_end_date = Column(DateTime, default=now_utc())
    planned_start_date = Column(DateTime, default=now_utc())
    planned_end_date = Column(DateTime, default=now_utc())
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class ProjectView(Base):
    __tablename__ = "vw_project"
    business_unit_id = Column(String(10))
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    project_id = Column(String(10), primary_key=True, index=True)
    project_name = Column(String(100))
    project_description = Column(String(4000))
    delivery_manager_id = Column(String(10))
    delivery_manager_name = Column(String(100))
    baseline_start_date = Column(DateTime)
    baseline_end_date = Column(DateTime)
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class Deliverable(Base):
    __tablename__ = "deliverable"
    deliverable_id = Column(String(10), primary_key=True, index=True)
    project_id = Column(String(10))
    deliverable_name = Column(String(100))
    deliverable_description = Column(String(4000))
    priority = Column(String(100))
    baseline_start_date = Column(DateTime, default=now_utc())
    baseline_end_date = Column(DateTime, default=now_utc())
    planned_start_date = Column(DateTime, default=now_utc())
    planned_end_date = Column(DateTime, default=now_utc())
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class DeliverableView(Base):
    __tablename__ = "vw_deliverable"
    business_unit_id = Column(String(10))
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    project_id = Column(String(10))
    project_name = Column(String(100))
    delivery_manager_id = Column(String(10))
    delivery_manager_name = Column(String(100))
    deliverable_id = Column(String(10), primary_key=True, index=True)
    deliverable_name = Column(String(100))
    deliverable_description = Column(String(4000))
    priority = Column(String(100))
    baseline_start_date = Column(DateTime)
    baseline_end_date = Column(DateTime)
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class Task(Base):
    __tablename__ = "task"
    task_id = Column(String(10), primary_key=True, index=True)
    deliverable_id = Column(String(10))
    task_name = Column(String(100))
    task_description = Column(String(4000))
    task_type_id = Column(String(10))
    priority = Column(String(100))
    baseline_start_date = Column(DateTime, default=now_utc())
    baseline_end_date = Column(DateTime, default=now_utc())
    planned_start_date = Column(DateTime, default=now_utc())
    planned_end_date = Column(DateTime, default=now_utc())
    effort_estimated_in_hours = Column(String(10))
    assignee_id = Column(String(10))
    reviewer_id = Column(String(10))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class TaskView(Base):
    __tablename__ = "vw_task"
    business_unit_id = Column(String(10))
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    project_id = Column(String(10))
    project_name = Column(String(100))
    delivery_manager_id = Column(String(10))
    delivery_manager_name = Column(String(100))
    deliverable_id = Column(String(10))
    deliverable_name = Column(String(100))
    task_id = Column(String(10), primary_key=True, index=True)
    task_name = Column(String(100))
    task_description = Column(String(4000))
    task_type_id = Column(String(10))
    task_type_name = Column(String(100))
    priority = Column(String(100))
    baseline_start_date = Column(DateTime)
    baseline_end_date = Column(DateTime)
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    effort_estimated_in_hours = Column(String(10))
    assignee_id = Column(String(10))
    assignee_name = Column(String(100))
    reviewer_id = Column(String(10))
    reviewer_name = Column(String(100))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class TaskType(Base):
    __tablename__ = "task_type"
    task_type_id = Column(String(10), primary_key=True, index=True)
    task_type_Name = Column(String(100))
    task_type_description = Column(String(4000))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class TaskTypeView(Base):
    __tablename__ = "vw_task_type"
    task_type_id = Column(String(10), primary_key=True, index=True)
    task_type_Name = Column(String(100))
    task_type_description = Column(String(4000))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class TaskStatus(Base):
    __tablename__ = "task_status"
    task_status_id = Column(String(10), primary_key=True, index=True)
    task_id = Column(String(10))
    action_date = Column(Date)
    hours_spent = Column(String(10))
    progress = Column(String(10))
    remarks = Column(String(4000))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    entity_status = Column(String(10), default="Active")
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))


class TaskStatusView(Base):
    __tablename__ = "vw_task_status_latest"
    business_unit_id = Column(String(10))
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    project_id = Column(String(10))
    project_name = Column(String(100))
    delivery_manager_id = Column(String(10))
    delivery_manager_name = Column(String(100))
    deliverable_id = Column(String(10))
    deliverable_name = Column(String(100))
    task_id = Column(String(10))
    task_name = Column(String(100))
    task_status_id = Column(String(10), primary_key=True, index=True)
    action_date = Column(Date)
    hours_spent = Column(String(10))
    progress = Column(String(10))
    remarks = Column(String(4000))
    updated_at = Column(DateTime)
    updated_by_name = Column(String(100))
    updated_by = Column(String(100))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    entity_status = Column(String(10))


class Issue(Base):
    __tablename__ = "issue"
    issue_id = Column(String(10), primary_key=True, index=True)
    task_id = Column(String(10))
    issue_title = Column(String(100))
    issue_description = Column(String(4000))
    action_owner_id = Column(String(10))
    issue_priority = Column(String(100))
    issue_status = Column(String(100))
    created_at = Column(DateTime, default=now_utc())
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")


class IssueView(Base):
    __tablename__ = "vw_issue"
    business_unit_id = Column(String(10))
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    project_id = Column(String(10))
    project_name = Column(String(100))
    delivery_manager_id = Column(String(10))
    delivery_manager_name = Column(String(100))
    deliverable_id = Column(String(10))
    deliverable_name = Column(String(100))
    task_id = Column(String(10))
    task_name = Column(String(100))
    issue_id = Column(String(10), primary_key=True, index=True)
    issue_title = Column(String(100))
    issue_description = Column(String(4000))
    issue_priority = Column(String(100))
    issue_status = Column(String(100))
    action_owner_id = Column(String(10))
    action_owner_name = Column(String(100))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class IssueActivity(Base):
    __tablename__ = "issue_activity"
    issue_activity_id = Column(String(10), primary_key=True, index=True)
    issue_id = Column(String(10))
    comment_by = Column(String(10))
    comment_at = Column(DateTime, default=now_utc())
    comment = Column(String(4000))
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now_utc())
    updated_by = Column(String(10))
    created_at = Column(DateTime, default=now_utc())
    entity_status = Column(String(10), default="Active")


class IssueActivityView(Base):
    __tablename__ = "vw_issue_activity"
    business_unit_id = Column(String(10))
    business_unit_name = Column(String(100))
    business_unit_head_id = Column(String(10))
    business_unit_head_name = Column(String(100))
    project_id = Column(String(10))
    project_name = Column(String(100))
    delivery_manager_id = Column(String(10))
    delivery_manager_name = Column(String(100))
    deliverable_id = Column(String(10))
    deliverable_name = Column(String(100))
    task_id = Column(String(10))
    task_name = Column(String(100))
    issue_id = Column(String(10))
    issue_activity_id = Column(String(10), primary_key=True, index=True)
    comment_by = Column(String(10))
    comment_by_name = Column(String(100))
    comment_at = Column(DateTime)
    comment = Column(String(4000))
    created_at = Column(DateTime)
    created_by = Column(String(10))
    created_by_name = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(10))
    updated_by_name = Column(String(100))
    entity_status = Column(String(10))


class AuditLog(Base):
    __tablename__ = "audit_log"
    audit_id = Column(String(10), primary_key=True, index=True)
    entity_type = Column(String(100))
    entity_id = Column(String(10))
    action = Column(String(100))
    field_changed = Column(String(100))
    old_value = Column(String(1000), default="NA")
    new_value = Column(String(1000), default="NA")
    changed_by = Column(String(10))
    changed_at = Column(DateTime, default=now_utc())
