import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog, User


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def write_audit(
    session: AsyncSession,
    action_code: str,
    details: dict[str, Any],
    actor_user: User | None = None,
) -> AuditLog:
    row = AuditLog(
        actor_user_id=actor_user.id if actor_user else None,
        action_code=action_code,
        details_json=json.dumps(details, ensure_ascii=True),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row
