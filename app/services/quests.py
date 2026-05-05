from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Quest, User, UserQuestProgress


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_default_quests(session: AsyncSession) -> None:
    defaults = [
        ("tap_500", "Tap 500 total", "lifetime_taps", 500, 300.0, 0.0),
        ("tap_5000", "Tap 5000 total", "lifetime_taps", 5000, 5000.0, 80.0),
        ("pph_5k", "Reach 5000 PPH", "profit_per_hour", 5000, 12000.0, 250.0),
    ]
    for code, title, quest_type, target, reward_tokens, reward_pph in defaults:
        stmt = select(Quest).where(Quest.code == code)
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if existing:
            continue
        session.add(
            Quest(
                code=code,
                title=title,
                quest_type=quest_type,
                target_value=target,
                reward_tokens=reward_tokens,
                reward_pph=reward_pph,
                is_active=True,
            )
        )
    await session.commit()


async def list_active_quests(session: AsyncSession) -> list[Quest]:
    current = now_utc()
    stmt = select(Quest).where(Quest.is_active.is_(True))
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    active: list[Quest] = []
    for row in rows:
        if row.starts_at and row.starts_at > current:
            continue
        if row.expires_at and row.expires_at < current:
            continue
        active.append(row)
    return active


def quest_progress_value(user: User, quest: Quest) -> int:
    if quest.quest_type == "lifetime_taps":
        return user.lifetime_taps
    if quest.quest_type == "profit_per_hour":
        return int(user.profit_per_hour)
    if quest.quest_type == "daily_taps":
        return user.daily_taps
    return 0


async def update_progress(session: AsyncSession, user: User) -> list[UserQuestProgress]:
    active = await list_active_quests(session)
    changed: list[UserQuestProgress] = []
    for quest in active:
        stmt = select(UserQuestProgress).where(UserQuestProgress.user_id == user.id, UserQuestProgress.quest_id == quest.id)
        row = (await session.execute(stmt)).scalar_one_or_none()
        value = quest_progress_value(user, quest)
        if not row:
            row = UserQuestProgress(user_id=user.id, quest_id=quest.id, current_value=value, is_completed=value >= quest.target_value)
            session.add(row)
        else:
            row.current_value = value
            if not row.is_completed and value >= quest.target_value:
                row.is_completed = True
        changed.append(row)
    await session.commit()
    return changed


async def claim_quest(session: AsyncSession, user: User, quest_code: str) -> tuple[bool, str]:
    quest_stmt = select(Quest).where(Quest.code == quest_code, Quest.is_active.is_(True))
    quest = (await session.execute(quest_stmt)).scalar_one_or_none()
    if not quest:
        return False, "Quest not found"
    row_stmt = select(UserQuestProgress).where(UserQuestProgress.user_id == user.id, UserQuestProgress.quest_id == quest.id)
    progress = (await session.execute(row_stmt)).scalar_one_or_none()
    if not progress or not progress.is_completed:
        return False, "Quest not completed"
    if progress.claimed_at:
        return False, "Already claimed"
    user.total_tokens += quest.reward_tokens
    user.profit_per_hour += quest.reward_pph
    progress.claimed_at = now_utc()
    await session.commit()
    return True, f"Claimed {quest.reward_tokens} tokens and {quest.reward_pph} PPH"


def format_quests(rows: list[Quest], progress_map: dict[int, UserQuestProgress]) -> str:
    if not rows:
        return "No active quests"
    lines: list[str] = ["Quest board"]
    for quest in rows:
        progress = progress_map.get(quest.id)
        value = progress.current_value if progress else 0
        mark = "done" if progress and progress.is_completed else "pending"
        lines.append(f"{quest.code}: {quest.title} | {value}/{quest.target_value} | {mark}")
    return "\n".join(lines)
