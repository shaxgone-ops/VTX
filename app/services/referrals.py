from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Referral, User

settings = get_settings()


async def register_referral(session: AsyncSession, inviter: User, invitee: User) -> bool:
    if inviter.id == invitee.id:
        return False
    stmt = select(Referral).where(Referral.inviter_id == inviter.id, Referral.invitee_id == invitee.id)
    result = await session.execute(stmt)
    exists = result.scalar_one_or_none()
    if exists:
        return False
    referral = Referral(inviter_id=inviter.id, invitee_id=invitee.id, reward_paid=True)
    inviter.total_tokens += settings.referral_reward
    session.add(referral)
    await session.commit()
    return True
