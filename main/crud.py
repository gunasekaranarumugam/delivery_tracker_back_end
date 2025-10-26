from datetime import datetime
from main import models

"""def audit_log(
    db, 
    entity_type: str, 
    entity_id: str, 
    action: str, 
    field_changed: str = None, 
    previous_value: str = None, 
    new_value: str = None, 
    action_performed_by: str = 'system'
):
    al = models.AuditLog(
        AuditLogId=f"AUD-{int(datetime.utcnow().timestamp() * 1000)}",
        EntityType=entity_type,
        EntityId=entity_id,
        Action=action,
        FieldChanged=field_changed,
        PreviousValue=previous_value,
        NewValue=new_value,
        ActionPerformedBy=action_performed_by,
        ActionPerformedAt=datetime.utcnow()
    )
    db.add(al)
    db.commit()"""

from datetime import datetime
from sqlalchemy.orm import Session

def audit_log(
    db: Session,
    table_name: str,
    record_id: str,
    action: str,
    changed_by: str = 'system',
    details: str = None
):
    al = models.AuditLog(
        AuditLogId=f"AUD-{int(datetime.utcnow().timestamp() * 1000)}",
        TableName=table_name,
        RecordId=record_id,
        Action=action,
        UserId=changed_by,
        Timestamp=datetime.utcnow(),
        Details=details,
    )
    db.add(al)
    db.commit()

