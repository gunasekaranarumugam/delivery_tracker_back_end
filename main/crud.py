import uuid
from datetime import datetime
from main import models
from datetime import datetime
import uuid


def audit_log(db, entity_type, entity_id, action, changed_by, field_changed=None, old_value=None, new_value=None):
    if not field_changed:
        field_changed = "ALL"

    al = models.AuditLog(
        audit_id=str(uuid.uuid4()),  # <-- Guaranteed unique
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by,
        changed_at=datetime.utcnow()
    )
    db.add(al)
    db.commit()
