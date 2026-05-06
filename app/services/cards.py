"""
VTX Earn Arena — Card Service
==============================
Handles card catalog seeding (305 cards), listing,
upgrade logic, and daily combo system.

Upgrade cost formula:
  cost(stage) = base_cost × 3^(stage − 1)

Profit per hour at each stage is linearly interpolated:
  stage 1  → stage_profit_min
  stage 15 → stage_profit_max
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.cards_catalog import (
    ALL_CATEGORIES,
    RARITY_PROFIT_RANGES,
    card_image_url,
)
from app.models import (
    CardDefinition,
    DailyCombo,
    User,
    UserCard,
    UserDailyComboStatus,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
COST_MULTIPLIER = 3.0          # Each stage costs 300% more
MAX_STAGE = 15                 # Maximum upgrade level


# ---------------------------------------------------------------------------
# Seed the card catalog into the database
# ---------------------------------------------------------------------------

async def ensure_default_cards(session: AsyncSession) -> int:
    """
    Insert all 305 cards from the catalog into the database.
    Only inserts cards that don't already exist (by code).
    Returns the number of newly inserted cards.
    """
    # Check if we already have cards in the database
    count_result = await session.execute(
        select(func.count()).select_from(CardDefinition)
    )
    existing_count = count_result.scalar() or 0

    # If we already have 300+ cards, skip seeding
    if existing_count >= 300:
        return 0

    inserted = 0
    sort_idx = 0

    for category, card_list in ALL_CATEGORIES.items():
        for code, title, rarity, base_cost, description in card_list:
            # Check if this specific card already exists
            stmt = select(CardDefinition).where(CardDefinition.code == code)
            exists = (await session.execute(stmt)).scalar_one_or_none()
            if exists:
                sort_idx += 1
                continue

            # Look up profit range for this rarity
            profit_min, profit_max = RARITY_PROFIT_RANGES.get(
                rarity, (40_000.0, 55_000.0)
            )

            # Create the card definition
            card = CardDefinition(
                code=code,
                title=title,
                category=category,
                rarity=rarity,
                description=description,
                image_url=card_image_url(code),
                base_cost=base_cost,
                stage_profit_min=profit_min,
                stage_profit_max=profit_max,
                max_stage=MAX_STAGE,
                sort_order=sort_idx,
                is_active=True,
            )
            session.add(card)
            inserted += 1
            sort_idx += 1

    if inserted > 0:
        await session.commit()
        logger.info("Seeded %d new cards into database", inserted)

    return inserted


# ---------------------------------------------------------------------------
# Upgrade cost calculation
# ---------------------------------------------------------------------------

def upgrade_cost(base_cost: float, next_stage: int) -> float:
    """
    Calculate the cost to upgrade to the given stage.
    Formula: base_cost × 3^(stage − 1)

    Examples for base_cost=100:
      Stage 1:  100
      Stage 2:  300
      Stage 3:  900
      Stage 5:  8,100
      Stage 10: 1,968,300
      Stage 15: 478,296,900
    """
    if next_stage <= 0:
        return 0.0
    return round(base_cost * (COST_MULTIPLIER ** (next_stage - 1)), 4)


# ---------------------------------------------------------------------------
# Profit per hour at a given stage
# ---------------------------------------------------------------------------

def stage_profit(card: CardDefinition, stage: int) -> float:
    """
    Linear interpolation of profit per hour between min and max.
    Stage 0 → 0 PPH (not purchased yet)
    Stage 1 → stage_profit_min
    Stage 15 → stage_profit_max
    """
    if stage <= 0:
        return 0.0

    span = card.stage_profit_max - card.stage_profit_min
    if span <= 0:
        return card.stage_profit_min

    # Progress from 0.0 (stage 1) to 1.0 (stage max_stage)
    progress = (stage - 1) / max(1, card.max_stage - 1)
    return round(card.stage_profit_min + span * progress, 4)


# ---------------------------------------------------------------------------
# List cards with user's current stage
# ---------------------------------------------------------------------------

async def list_cards_with_user_stage(
    session: AsyncSession,
    user: User,
    category: str | None = None,
) -> list[dict]:
    """
    Return all active cards with the user's current upgrade stage.
    Optionally filter by category.
    """
    stmt = select(CardDefinition).where(
        CardDefinition.is_active.is_(True)
    ).order_by(CardDefinition.sort_order)

    if category:
        stmt = stmt.where(CardDefinition.category == category)

    cards = list((await session.execute(stmt)).scalars().all())

    # Fetch all user cards in one query for efficiency
    user_cards = list(
        (await session.execute(
            select(UserCard).where(UserCard.user_id == user.id)
        )).scalars().all()
    )
    user_map = {uc.card_id: uc for uc in user_cards}

    response: list[dict] = []
    for card in cards:
        owned = user_map.get(card.id)
        current_stage = owned.stage if owned else 0
        next_stg = min(card.max_stage, current_stage + 1)
        cost = 0.0 if current_stage >= card.max_stage else upgrade_cost(
            card.base_cost, next_stg
        )

        response.append({
            "card_id": card.id,
            "code": card.code,
            "title": card.title,
            "category": card.category,
            "rarity": card.rarity,
            "description": card.description,
            "image_url": card.image_url,
            "stage": current_stage,
            "max_stage": card.max_stage,
            "current_profit": stage_profit(card, current_stage),
            "next_profit": stage_profit(card, next_stg),
            "next_cost": cost,
            "total_spent": owned.total_spent if owned else 0,
        })

    return response


# ---------------------------------------------------------------------------
# List available categories
# ---------------------------------------------------------------------------

async def list_categories(session: AsyncSession) -> list[dict]:
    """Return category names and card counts."""
    from app.data.cards_catalog import CATEGORY_DISPLAY_NAMES

    stmt = (
        select(
            CardDefinition.category,
            func.count(CardDefinition.id).label("count"),
        )
        .where(CardDefinition.is_active.is_(True))
        .group_by(CardDefinition.category)
    )
    rows = (await session.execute(stmt)).all()

    return [
        {
            "key": row.category,
            "name": CATEGORY_DISPLAY_NAMES.get(row.category, row.category),
            "count": row.count,
        }
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Upgrade a card
# ---------------------------------------------------------------------------

async def upgrade_user_card(
    session: AsyncSession,
    user: User,
    card_id: int,
) -> tuple[bool, str, dict | None]:
    """
    Upgrade a user's card to the next stage.
    Returns (success, message, data_dict).
    """
    # Find the card definition
    card = (
        await session.execute(
            select(CardDefinition).where(
                CardDefinition.id == card_id,
                CardDefinition.is_active.is_(True),
            )
        )
    ).scalar_one_or_none()

    if not card:
        return False, "Card not found", None

    # Find or create user's card record
    user_card = (
        await session.execute(
            select(UserCard).where(
                UserCard.user_id == user.id,
                UserCard.card_id == card.id,
            )
        )
    ).scalar_one_or_none()

    if not user_card:
        user_card = UserCard(
            user_id=user.id,
            card_id=card.id,
            stage=0,
            total_spent=0,
        )
        session.add(user_card)
        await session.flush()

    # Check if already at max stage
    if user_card.stage >= card.max_stage:
        return False, "Card already at maximum stage", None

    # Calculate upgrade cost
    next_stage = user_card.stage + 1
    cost = upgrade_cost(card.base_cost, next_stage)

    # Check balance
    if user.total_tokens < cost:
        return (
            False,
            f"Insufficient balance. Need {cost:,.2f}, have {user.total_tokens:,.2f}",
            None,
        )

    # Perform upgrade
    old_profit = stage_profit(card, user_card.stage)
    new_profit = stage_profit(card, next_stage)
    delta_profit = new_profit - old_profit

    user.total_tokens -= cost
    user_card.stage = next_stage
    user_card.total_spent += cost
    user.profit_per_hour += delta_profit

    await session.commit()

    return True, "Upgrade successful", {
        "card_id": card.id,
        "card_title": card.title,
        "card_rarity": card.rarity,
        "new_stage": user_card.stage,
        "max_stage": card.max_stage,
        "cost": round(cost, 4),
        "delta_profit": round(delta_profit, 4),
        "new_profit": round(new_profit, 4),
        "profit_per_hour": round(user.profit_per_hour, 4),
        "balance": round(user.total_tokens, 4),
    }


# ---------------------------------------------------------------------------
# Daily Combo helpers
# ---------------------------------------------------------------------------

def _today_key() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def get_daily_combo(session: AsyncSession) -> DailyCombo | None:
    """Get today's daily combo (3 cards to find)."""
    stmt = select(DailyCombo).where(DailyCombo.date_key == _today_key())
    return (await session.execute(stmt)).scalar_one_or_none()


async def check_daily_combo(
    session: AsyncSession, user: User
) -> tuple[bool, str, float]:
    """
    Check if user has upgraded all 3 combo cards today.
    Returns (all_found, message, reward_if_claimed).
    """
    combo = await get_daily_combo(session)
    if not combo:
        return False, "No daily combo set for today", 0

    # Check if already claimed
    status = (
        await session.execute(
            select(UserDailyComboStatus).where(
                UserDailyComboStatus.user_id == user.id,
                UserDailyComboStatus.date_key == _today_key(),
            )
        )
    ).scalar_one_or_none()

    if status and status.is_claimed:
        return False, "Already claimed today's combo", 0

    # Check if user owns all 3 cards
    target_ids = [combo.card_id_1, combo.card_id_2, combo.card_id_3]
    user_cards = list(
        (await session.execute(
            select(UserCard).where(
                UserCard.user_id == user.id,
                UserCard.card_id.in_(target_ids),
                UserCard.stage >= 1,
            )
        )).scalars().all()
    )

    owned_ids = {uc.card_id for uc in user_cards}
    missing = [cid for cid in target_ids if cid not in owned_ids]

    if missing:
        return False, f"Missing {len(missing)} combo card(s)", 0

    # All found — claim reward
    if not status:
        status = UserDailyComboStatus(
            user_id=user.id,
            date_key=_today_key(),
        )
        session.add(status)

    status.is_claimed = True
    status.claimed_at = datetime.now(timezone.utc)
    user.total_tokens += combo.reward_tokens
    await session.commit()

    return True, "Daily combo claimed!", combo.reward_tokens
