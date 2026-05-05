from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def top_by_balance(session: AsyncSession, limit: int = 10) -> list[User]:
    stmt = select(User).where(User.is_banned.is_(False)).order_by(desc(User.total_tokens)).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def top_by_pph(session: AsyncSession, limit: int = 10) -> list[User]:
    stmt = select(User).where(User.is_banned.is_(False)).order_by(desc(User.profit_per_hour)).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


def format_leaderboard(rows: list[User], metric: str) -> str:
    if not rows:
        return "No leaderboard data yet."
    lines: list[str] = [f"Top {metric}"]
    for idx, row in enumerate(rows, start=1):
        name = row.username or row.first_name or f"user_{row.telegram_id}"
        value = row.total_tokens if metric == "balance" else row.profit_per_hour
        lines.append(f"{idx}. {name}: {round(value, 4)}")
    return "\n".join(lines)
