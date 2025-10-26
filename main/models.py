from sqlalchemy import Column, String, Integer, Date, DateTime, Text, Boolean, CheckConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DECIMAL, Numeric
import datetime

Base = declarative_base()

def now():
    return datetime.datetime.utcnow()

class Employee(Base):
    __tablename__ = "employee"
    employee_id = Column(String(10), primary_key=True, index=True)
    employee_full_name = Column(String(100))
    employee_email_address = Column(String(100))
    password = Column(String(100))
    business_unit_id = Column(String(10)) 
    holiday_calendar_id = Column(String(10)) 
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")

class BusinessUnit(Base):
    __tablename__ = "business_unit"
    business_unit_id = Column(String(10), primary_key=True, index=True)
    business_unit_name = Column(String(100)) 
    business_unit_head_id= Column(String(10)) 
    business_unit_description = Column(String(4000))
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")
    
class Project(Base):
    __tablename__ = "project"
    project_id = Column(String(10),primary_key=True,index=True)
    business_unit_id = Column(String(10))
    project_name = Column(String(100))
    project_description = Column(String(4000))
    delivery_manager_id = Column(String(10))
    baseline_start_date = Column(DateTime,default=now) 
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now) 
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")
    
class Deliverable(Base): 
    __tablename__ = "deliverable"
    deliverable_id = Column(String(10),primary_key=True,index=True)
    project_id = Column(String(10))
    deliverbale_name = Column(String(100))
    deliverable_description = Column(String(4000))
    priority = Column(String(100))
    baseline_start_date = Column(DateTime,default=now)
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now) 
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")

class Task(Base): 
    __tablename__ = "task"
    task_id = Column(String(10), primary_key=True, index=True)
    deliverable_id = Column(String(10))
    task_name = Column(String(100))
    task_description = Column(String(4000)) 
    task_type_id = Column(String(10))
    priority = Column(String(100))
    baseline_start_date = Column(DateTime,default=now) 
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    estimated_effort_in_hours = Column(String(10))
    assignee_id = Column(String(10))
    reviewer_id = Column(String(10)) 
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")

class TaskTypeMaster(Base):
    __tablename__ = "task_type_master"
    task_type_id = Column(String(10), primary_key=True, index=True)
    task_type_Name = Column(String(100))
    task_type_description = Column(String(4000))
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))
    entity_status = Column(String(10), default="Active")

class TaskStatus(Base):
    __tablename__ = "task_status"
    task_status_id = Column(String(10), primary_key=True, index=True)
    task_id = Column(String(10))
    action_date = Column(Date)
    hours_spent = Column(String(10))
    progress = Column(String(10))
    remarks = Column(String(4000))
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))

class Issue(Base):
    __tablename__ = "issue"
    issue_id = Column(String(10), primary_key=True, index=True)
    task_id = Column(String(10))
    issue_title = Column(String(100))
    issue_description = Column(String(4000))
    action_owner_id = Column(String(10))
    priority = Column(String(100))
    status = Column(String(100))
    created_at = Column(DateTime, default=now)
    created_by = Column(String(10))
    updated_at = Column(DateTime, default=now)
    updated_by = Column(String(10))

class IssueActivity(Base):
    __tablename__ = "issue_activity"
    issue_activity_id = Column(String(10), primary_key=True, index=True)
    issueId = Column(String(10))
    comment_by = Column(String(10))
    comment_at = Column(DateTime, default=now)
    comment = Column(String(4000))

class AuditLog(Base): 
    __tablename__ = "audit_log"
    audit_id = Column(String(10), primary_key=True, index=True)
    entity_type = Column(String(100))
    entity_id = Column(String(10))
    action = Column(String(100))
    field_changed = Column(String(100))
    old_value = Column(String(1000), nullable=True)
    new_value = Column(String(1000), nullable=True)
    changed_by = Column(String(10))
    changed_at = Column(DateTime, default=now)
