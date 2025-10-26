class BusinessUnit(Base):
    __tablename__ = "business_unit"

    business_unit_id = Column(String(50), primary_key=True, index=True)
    business_unit_name = Column(String(200))
    business_unit_head_id= Column(String(50),ForeignKey('employee.EmployeeId'),nullable=False)
    business_unit_description = Column(Text, nullable=True)
    entitystatus = Column(String(50), default="Active")
    createdat = Column(DateTime, default=now)
    updatedat = Column(DateTime, default=now)
    createdby = Column(String(50),ForeignKey('user.user_id'))

class User(Base):
    __tablename__ = "user"
    user_id = Column(String(50),primary_key=True,index=True)
    full_name = Column(String(200))
    email_address = Column(String(200))
    password = Column(String(200))
    entitystatus = Column(String(50), default="Active")
    createdat = Column(DateTime, default=now)
    updatedat = Column(DateTime, default=now)
    createdby = Column(String(50),ForeignKey('user.user_id'))

class Project(Base):
    __tablename__ = "project"

    project_id = Column(String(50),primary_key=True,index=True)
    business_unit_id = Column(String(50),ForeignKey('business_unit.business_unit_id'))
    project_name = Column(String(200))
    project_description = Column(String(200))
    delivery_manager_id = Column(String(50),ForeignKey('employee.employee_id'))
    baseline_start_date = Column(DateTime,default=now)
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    entitystatus = Column(String(50), default="Active")
    createdat = Column(DateTime, default=now)
    updatedat = Column(DateTime, default=now)
    createdby = Column(String(50),ForeignKey('user.user_id'))

class Deliverable:
    __tablename__ = "deliverable"

    deliverable_id = Column(String(50),primary_key=True,index=True)
    project_id = Column(String(50),ForeignKey("project.project_id"))
    deliverbale_name = Column(String(50))
    deliverable_description = Column(String(50))
    priority = Column(String(50))
    baseline_start_date = Column(DateTime,default=now)
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    entitystatus = Column(String(50), default="Active")
    createdat = Column(DateTime, default=now)
    updatedat = Column(DateTime, default=now)
    createdby = Column(String(50),ForeignKey('user.user_id'))

class Task(Base):
    __tablename__ = "task"

    task_id = Column(String(50), primary_key=True, index=True)
    deliverable_id = Column(String(50), ForeignKey('deliverable.deliverbale_id'))
    task_type_id = Column(String(50),ForeignKey('task_type_master.TaskTypeId'))
    task_name = Column(String(300))
    task_description = Column(String(200))
    assigne_id = Column(String(50), ForeignKey('employee.EmployeeId'), nullable=True)
    reviewer_id = Column(String(50), ForeignKey('employee.EmployeeId'), nullable=True)
    priority = Column(String(200))
    estimated_effort_in_hours = Column(DECIMAL(6,2))
    baseline_start_date = Column(DateTime,default=now)
    baseline_end_date = Column(DateTime,default=now)
    plan_start_date = Column(DateTime,default=now)
    plan_end_date = Column(DateTime,default=now)
    entitystatus = Column(String(50), default="Active")
    createdat = Column(DateTime, default=now)
    updatedat = Column(DateTime, default=now)
    createdby = Column(String(50),ForeignKey('user.user_id'))

class AuditLog:
    __tablename__ = "audit_log"

    audit_id = Column(String(80), primary_key=True, index=True)
    entity_type = Column(String(200))
    entity_id = Column(String(200))
    action = Column(String(100))
    field_changed = Column(String(200), nullable=True)
    old_value = Column(String(1000), nullable=True)
    new_value = Column(String(1000), nullable=True)
    changed_by = Column(String(200), nullable=True)
    createdat = Column(DateTime, default=now)
   





