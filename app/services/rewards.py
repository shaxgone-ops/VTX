from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import TapEvent, User

settings = get_settings()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def award_daily_active_bonus(session: AsyncSession, user: User) -> bool:
    boundary = now_utc() - timedelta(hours=24)
    stmt = select(TapEvent).where(TapEvent.user_id == user.id, TapEvent.created_at >= boundary).limit(1)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()
    if not event:
        return False
    user.total_tokens += settings.daily_active_reward
    await session.commit()
    return True


async def boost_profit_per_hour(session: AsyncSession, user: User, delta: int) -> User:
    user.profit_per_hour += delta
    await session.commit()
    await session.refresh(user)
    return user
