import json
import uuid
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


def record_audit(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str,
    actor_user_id: Optional[str] = None,
    reason: Optional[str] = None,
    changes: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> AuditEvent:
    event = AuditEvent(
        id=str(uuid.uuid4()),
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        reason=reason,
        change_summary=json.dumps(changes, default=str, sort_keys=True) if changes else None,
        correlation_id=correlation_id,
    )
    db.add(event)
    return event
