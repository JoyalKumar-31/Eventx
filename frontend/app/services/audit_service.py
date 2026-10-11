import json
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    user_id: Optional[int] = None,
    old_values: Optional[Any] = None,
    new_values: Optional[Any] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Record an audit trail entry for system operations."""
    try:
        old_str = json.dumps(old_values, default=str) if isinstance(old_values, (dict, list)) else (str(old_values) if old_values is not None else None)
        new_str = json.dumps(new_values, default=str) if isinstance(new_values, (dict, list)) else (str(new_values) if new_values is not None else None)

        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            old_values=old_str,
            new_values=new_str,
            ip_address=ip_address,
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry
    except Exception as e:
        db.rollback()
        # Fail gracefully without breaking main transaction
        return None
