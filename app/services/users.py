from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User

settings = get_settings()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def apply_stamina_regen(user: User) -> None:
    current = now_utc()
    last = user.last_stamina_sync_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    elapsed_minutes = max(0, int((current - last) / timedelta(minutes=1)))
    regen = elapsed_minutes * settings.stamina_regen_per_min
    max_stamina = settings.initial_stamina
    if regen > 0:
        user.stamina = min(max_stamina, user.stamina + regen)
        user.last_stamina_sync_at = current


def reset_daily_if_needed(user: User) -> None:
    current = now_utc()
    last = user.last_daily_reset_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    if last.date() != current.date():
        user.daily_taps = 0
        user.last_daily_reset_at = current


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_or_update_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    invited_by_user_id: int | None = None,
) -> User:
    user = await get_user_by_telegram_id(session, telegram_id)
    if user:
        user.username = username
        user.first_name = first_name
        apply_stamina_regen(user)
        reset_daily_if_needed(user)
        await session.commit()
        await session.refresh(user)
        return user
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        invited_by_id=invited_by_user_id,
        is_vip=telegram_id in settings.vip_id_set,
        stamina=settings.initial_stamina,
        profit_per_hour=settings.base_profit_per_hour,
        locale="uz",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
