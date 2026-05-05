from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DeviceFingerprint, User


def hash_fingerprint(raw: str) -> str:
    return sha256(raw.encode("utf-8")).hexdigest()


async def register_fingerprint(session: AsyncSession, user: User, raw_fingerprint: str) -> tuple[bool, str]:
    fp_hash = hash_fingerprint(raw_fingerprint)
    stmt = select(DeviceFingerprint).where(DeviceFingerprint.user_id == user.id, DeviceFingerprint.fingerprint_hash == fp_hash)
    row = (await session.execute(stmt)).scalar_one_or_none()
    if row:
        return True, "Fingerprint already known"
    count_stmt = select(DeviceFingerprint).where(DeviceFingerprint.user_id == user.id)
    existing = list((await session.execute(count_stmt)).scalars().all())
    risk_flagged = len(existing) >= 4
    new_row = DeviceFingerprint(user_id=user.id, fingerprint_hash=fp_hash, risk_flagged=risk_flagged)
    session.add(new_row)
    if risk_flagged:
        user.suspicious_score += 12
    await session.commit()
    return True, "Fingerprint registered"
