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
from datetime import datetime
from typing import Optional, Union # Import Union/Optional
from pydantic import BaseModel, Field

# 1. FIX: Update EmployeeBase to allow str or None
class EmployeeBase(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    # === CRITICAL FIX: Allow None/null ===

    # ===================================
    password: str
    business_unit_id: str
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    entity_status: str

class EmployeeCreateAdmin(BaseModel): # Renamed for clarity vs. Register
    employee_id : str
    employee_full_name: str
    employee_email_address: str
    business_unit_id: str
  
    # NOTE: Password field is intentionally omitted for admin creation

class EmployeeRegister(BaseModel):
    employee_id : str
    employee_full_name: str
    employee_email_address: str
    password: str
    business_unit_id: str
    # NOTE: You may want this to be optional on register too if the UI doesn't require it
   

# ... EmployeeLogin is fine ...

# EmployeeRead inherits the fix from EmployeeBase, so it's now fine.
class EmployeeRead(EmployeeBase):
    class Config:
        orm_mode = True

# 2. FIX: Update EmployeeLoginResponse to allow str or None
class EmployeeLoginResponse(BaseModel):
    employee_id: str
    employee_full_name: str
    employee_email_address: str
    # === CRITICAL FIX: Allow None/null ===
  
    # ===================================
    auth_token: str

# EmployeePatch is fine, as it uses Optional which only applies to *incoming* data.
# However, you should align it with the base model for consistency:
class EmployeePatch(BaseModel):
    # Ensure this aligns with the base model if needed, but Optional[str] handles incoming None/missing keys.
    employee_id:str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
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
    deliverable_id:str
    deliverable_name: Optional[str] = None
    deliverable_description: Optional[str] = None
    priority: Optional[str]
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    entity_status: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    created_by: str
    updated_at: datetime = Field(default_factory=now)
    updated_by: str
    


class DeliverableRead(DeliverableBase):
    class Config:
        orm_mode = True


# =====================================================
# === Task Schemas ===
# =====================================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Assume 'now' is a function that returns the current time, as defined in your context
def now() -> datetime:
    return datetime.now()

# 1. CORE DATA SCHEMA - Defines all required, user-supplied, or system-relevant fields
class TaskBase(BaseModel):
    task_id:str
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
    reviewer_id: Optional[str] = None # Reviewer is often optional
    planned_start_date: datetime
    planned_end_date: datetime
    effort_estimated_in_hours: float
   


# 2. CREATE SCHEMA (POST Body) - Requires core data, omits generated IDs/timestamps
class TaskCreate(TaskBase):
    # Overriding optionality for fields that might be optional on creation
    task_id:str
    deliverable_id: str
    task_name: str
    task_description: str
    task_type_id: str
    priority: str
    baseline_start_date: datetime
    baseline_end_date: datetime
    planned_start_date: datetime
    planned_end_date: datetime
    effort_estimated_in_hours: int
    assignee_id: str
    reviewer_id: str # Reviewer is often optional
   
    
    


# 3. PATCH SCHEMA (PATCH Body) - Allows partial update of any field
class TaskPatch(BaseModel):
    # TaskBase fields, all made optional
    deliverable_id: Optional[str] = None
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    task_type_id: Optional[str] = None
    priority: Optional[str] = None
    baseline_start_date: Optional[datetime] = None
    baseline_end_date: Optional[datetime] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    effort_estimated_in_hours: Optional[float] = None
    assignee_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    
    # System fields that can be manually patched (e.g., status)
    entity_status: Optional[str] = None
    # No need for TaskUpdate, TaskPatch covers partial updates correctly.


# 4. READ SCHEMA (GET Response) - Full model, including generated system data
class TaskRead(TaskBase):
    task_id: str # Generated ID, mandatory for read
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
    reviewer_id: str # Reviewer is often optional
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    entity_status: str

    class Config:
        orm_mode = True


# =====================================================
# === Task Type Master Schemas ===
# =====================================================

# 1. CORE DATA SCHEMA
class TaskTypeBase(BaseModel):
    task_type_id: str
    task_type_Name: str
    task_type_description: Optional[str] = None


# 2. CREATE SCHEMA (POST Body) - All fields from base are sent
class TaskTypeCreate(TaskTypeBase):
    # Only task_type_id, task_type_Name are required, description is Optional
    pass


# 3. PATCH/UPDATE SCHEMA (PATCH Body) - Allows partial updates to mutable fields
# We only use one model for partial updates (PATCH)
class TaskTypePatch(BaseModel):
    task_type_Name: Optional[str] = None
    task_type_description: Optional[str] = None
    entity_status: Optional[str] = None
    # No need for TaskTypeMasterUpdate, as it was identical


# 4. READ SCHEMA (GET Response) - Full model
class TaskTypeRead(TaskTypeBase):
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    entity_status: str

    class Config:
        orm_mode = True
# =====================================================
# === Task Status Schemas ===
# =====================================================
# schemas/task_status.py (FastAPI Backend)
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from datetime import datetime, date # <-- Ensure 'date' is imported
# ...
# --- 1. TaskStatusCore: Defines ONLY the client-editable business fields ---
class TaskStatusCore(BaseModel):
    # Required for creation
    task_status_id:str
    task_id: str
    action_date: datetime
    progress: str
    hours_spent: str
    remarks: str
    
    # Optional/Defaulted
    entity_status: str = 'Active' # We can allow the client to set this or rely on a DB default

# --- 2. TaskStatusCreate: Payload for POST (No IDs or Audit fields) ---
class TaskStatusCreate(TaskStatusCore):
    pass 
    # The server will set task_status_id, created_at, and created_by

# --- 3. TaskStatusPatch: Payload for PATCH (Everything is optional) ---
class TaskStatusPatch(BaseModel):
    task_id: Optional[str] = None
    action_date: Optional[str] = None
    progress: Optional[str] = None
    hours_spent: Optional[str] = None
    remarks: Optional[str] = None
    entity_status: Optional[str] = None

# --- 4. TaskStatusRead: The Full Entity (Server Output) ---
# schemas/task_status.py (FIXED)

from typing import Optional # <--- Make sure this is imported

class TaskStatusRead(BaseModel):
    task_status_id: str
    task_id: Optional[str]
    action_date: datetime
    progress: str
    hours_spent: str
    remarks: str
    created_at: datetime
    
    # ✅ FIX: Change 'created_by' to Optional[str] to accept None from DB
    created_by: Optional[str] = None
    
    # You should also check the 'updated_by' field and potentially update it too
    # updated_by: Optional[str] = None 
    
    entity_status: str
    
    class Config:
        orm_mode = True


# =====================================================
# === Issue Schemas ===
# =====================================================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Utility function for default datetime (assuming 'now' is defined elsewhere)
def now():
    return datetime.now()

# --- 1. IssueCore: Defines the essential business fields (Matches Angular IssueCore) ---
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Utility function for default datetime (assuming 'now' is defined elsewhere)
def now():
    return datetime.now()

# --- 1. IssueCore: Defines the essential business fields (NO IDs or Audit Fields) ---
class IssueCore(BaseModel):
    # REQUIRED FIELDS
    task_id: str
    issue_title: str
    entity_status: str # e.g., 'Active', 'Archived'

    # OPTIONAL FIELDS
    issue_description: Optional[str] = None
    action_owner_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


# --- 2. IssueCreate: The Payload for POST /issues (Client Input) ---
# Inherits IssueCore. This is the exact payload Angular should send.
class IssueCreate(IssueCore):
    pass # Inherits only core fields. NO issue_id, created_at, etc.


# --- 3. IssuePatch: The Payload for PATCH/PUT (Partial Update) ---
# All fields from IssueCore are made optional using Partial.
class IssuePatch(BaseModel):
    # Use Optional[T] for every field to allow partial updates
    task_id: Optional[str] = None
    issue_title: Optional[str] = None
    entity_status: Optional[str] = None 
    issue_description: Optional[str] = None
    action_owner_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


# --- 4. IssueRead (The Full Entity returned by the API) ---
# This includes the core fields PLUS the server-managed fields.
class IssueRead(IssueCore):
    # PRIMARY ID
    issue_id: str 

    # AUDIT FIELDS (Server-managed)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)
    created_by: str
    updated_by: str

    class Config:
        orm_mode = True # Essential for mapping ORM objects
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

