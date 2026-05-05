from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def activate_vip(session: AsyncSession, user: User, days: int) -> User:
    start = now_utc()
    if user.vip_expires_at and user.vip_expires_at > start:
        start = user.vip_expires_at
    user.is_vip = True
    user.vip_expires_at = start + timedelta(days=days)
    await session.commit()
    await session.refresh(user)
    return user


async def sync_vip_expiry(session: AsyncSession, user: User) -> User:
    current = now_utc()
    if user.is_vip and user.vip_expires_at and user.vip_expires_at <= current:
        user.is_vip = False
    await session.commit()
    await session.refresh(user)
    return user
