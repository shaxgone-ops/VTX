from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import AirdropEpoch, AirdropSnapshot, User

settings = get_settings()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ScoreBreakdown:
    tap_score: float
    pph_score: float
    referral_score: float
    loyalty_score: float
    suspicious_penalty: float

    @property
    def total(self) -> float:
        return max(0.0, self.tap_score + self.pph_score + self.referral_score + self.loyalty_score - self.suspicious_penalty)


def user_score(user: User) -> ScoreBreakdown:
    tap_score = min(50000.0, user.lifetime_taps * 0.04)
    pph_score = min(30000.0, user.profit_per_hour * 0.7)
    referral_score = 0.0
    if user.invited_by_id:
        referral_score += 100.0
    loyalty_score = min(20000.0, (now_utc().replace(tzinfo=None) - user.created_at).days * 15.0)
    suspicious_penalty = user.suspicious_score * 3.5
    if user.is_banned:
        suspicious_penalty += 100000.0
    return ScoreBreakdown(
        tap_score=tap_score,
        pph_score=pph_score,
        referral_score=referral_score,
        loyalty_score=loyalty_score,
        suspicious_penalty=suspicious_penalty,
    )


async def open_or_get_monthly_epoch(session: AsyncSession, month_key: str, starts_at: datetime, ends_at: datetime, pool_tokens: float) -> AirdropEpoch:
    stmt = select(AirdropEpoch).where(AirdropEpoch.month_key == month_key)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        return existing
    row = AirdropEpoch(month_key=month_key, starts_at=starts_at, ends_at=ends_at, total_pool_tokens=pool_tokens, status="running")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def create_monthly_snapshot(session: AsyncSession, epoch: AirdropEpoch) -> int:
    users = list((await session.execute(select(User))).scalars().all())
    if not users:
        return 0
    scores: dict[int, float] = {}
    for user in users:
        breakdown = user_score(user)
        eligible = (not user.is_banned) and (user.suspicious_score < 120) and (user.total_tokens > 5)
        weighted = breakdown.total if eligible else 0.0
        scores[user.id] = weighted
    score_sum = sum(scores.values())
    count = 0
    for user in users:
        weighted = scores[user.id]
        proportional = 0.0 if score_sum == 0 else (weighted / score_sum) * epoch.total_pool_tokens
        bounded = max(settings.airdrop_reward_min, min(settings.airdrop_reward_max, proportional))
        reward = bounded if weighted > 0 else 0.0
        snapshot = AirdropSnapshot(
            epoch_id=epoch.id,
            user_id=user.id,
            weighted_score=weighted,
            airdrop_amount=round(reward, 6),
            is_eligible=weighted > 0,
        )
        session.add(snapshot)
        count += 1
    await session.commit()
    return count


async def apply_airdrop_rewards(session: AsyncSession, epoch: AirdropEpoch) -> int:
    stmt = select(AirdropSnapshot).where(AirdropSnapshot.epoch_id == epoch.id, AirdropSnapshot.is_eligible.is_(True))
    rows = list((await session.execute(stmt)).scalars().all())
    updated = 0
    for row in rows:
        user = (await session.execute(select(User).where(User.id == row.user_id))).scalar_one_or_none()
        if not user:
            continue
        user.total_tokens += row.airdrop_amount
        updated += 1
    epoch.status = "distributed"
    await session.commit()
    return updated
