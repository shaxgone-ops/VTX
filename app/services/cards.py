from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CardDefinition, User, UserCard

RARITY_TARGETS = {
    "common": (40000.0, 55000.0),
    "rare": (60000.0, 75000.0),
    "epic": (80000.0, 90000.0),
    "legendary": (90000.0, 100000.0),
}


async def ensure_default_cards(session: AsyncSession) -> None:
    defaults = [
        ("meme_doge", "Doge Reactor", "common", "https://images.unsplash.com/photo-1554412933-514a83d2f3c8?auto=format&fit=crop&w=1080&q=80", 120.0),
        ("meme_pepe", "Pepe Forge", "rare", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1080&q=80", 550.0),
        ("meme_shiba", "Shiba Matrix", "epic", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1080&q=80", 1500.0),
        ("meme_ai", "AI Whale Core", "legendary", "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1080&q=80", 5000.0),
    ]
    for code, title, rarity, image_url, base_cost in defaults:
        stmt = select(CardDefinition).where(CardDefinition.code == code)
        if (await session.execute(stmt)).scalar_one_or_none():
            continue
        min_profit, max_profit = RARITY_TARGETS[rarity]
        row = CardDefinition(
            code=code,
            title=title,
            rarity=rarity,
            image_url=image_url,
            base_cost=base_cost,
            stage_profit_min=min_profit,
            stage_profit_max=max_profit,
            max_stage=15,
            is_active=True,
        )
        session.add(row)
    await session.commit()


def upgrade_cost(base_cost: float, next_stage: int) -> float:
    return round(base_cost * (3 ** (next_stage - 1)), 4)


def stage_profit(card: CardDefinition, stage: int) -> float:
    if stage <= 0:
        return 0.0
    span = card.stage_profit_max - card.stage_profit_min
    if span <= 0:
        return card.stage_profit_min
    progress = (stage - 1) / max(1, card.max_stage - 1)
    return round(card.stage_profit_min + span * progress, 4)


async def list_cards_with_user_stage(session: AsyncSession, user: User) -> list[dict]:
    cards = list((await session.execute(select(CardDefinition).where(CardDefinition.is_active.is_(True)))).scalars().all())
    user_cards = list((await session.execute(select(UserCard).where(UserCard.user_id == user.id))).scalars().all())
    user_map = {row.card_id: row for row in user_cards}
    response: list[dict] = []
    for card in cards:
        owned = user_map.get(card.id)
        stage = owned.stage if owned else 0
        next_stage = min(card.max_stage, stage + 1)
        cost = 0.0 if stage >= card.max_stage else upgrade_cost(card.base_cost, next_stage)
        response.append(
            {
                "card_id": card.id,
                "code": card.code,
                "title": card.title,
                "rarity": card.rarity,
                "image_url": card.image_url,
                "stage": stage,
                "max_stage": card.max_stage,
                "current_profit": stage_profit(card, stage),
                "next_profit": stage_profit(card, next_stage),
                "next_cost": cost,
            }
        )
    return response


async def upgrade_user_card(session: AsyncSession, user: User, card_id: int) -> tuple[bool, str, dict | None]:
    card = (await session.execute(select(CardDefinition).where(CardDefinition.id == card_id, CardDefinition.is_active.is_(True)))).scalar_one_or_none()
    if not card:
        return False, "Card not found", None
    user_card = (await session.execute(select(UserCard).where(UserCard.user_id == user.id, UserCard.card_id == card.id))).scalar_one_or_none()
    if not user_card:
        user_card = UserCard(user_id=user.id, card_id=card.id, stage=0, total_spent=0)
        session.add(user_card)
        await session.flush()
    if user_card.stage >= card.max_stage:
        return False, "Card reached max stage", None
    next_stage = user_card.stage + 1
    cost = upgrade_cost(card.base_cost, next_stage)
    if user.total_tokens < cost:
        return False, "Insufficient balance", None
    user.total_tokens -= cost
    user_card.stage = next_stage
    user_card.total_spent += cost
    delta_profit = stage_profit(card, next_stage) - stage_profit(card, next_stage - 1)
    user.profit_per_hour += delta_profit
    await session.commit()
    return True, "Upgrade successful", {
        "card_id": card.id,
        "new_stage": user_card.stage,
        "cost": cost,
        "delta_profit": round(delta_profit, 4),
        "profit_per_hour": round(user.profit_per_hour, 4),
        "balance": round(user.total_tokens, 4),
    }
