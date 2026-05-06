"""
VTX Earn Arena — Web API (FastAPI routes)
==========================================
All REST endpoints for the Telegram Mini App frontend.

Endpoints:
  GET  /api/user/{telegram_id}       — user profile + offline earnings
  POST /api/tap                       — process tap event
  GET  /api/cards/{telegram_id}       — card list with user stages
  GET  /api/categories                — card category list
  POST /api/cards/upgrade             — upgrade a card
  GET  /api/leaderboard               — top 50 players
  GET  /api/referrals/{telegram_id}   — referral info
  GET  /api/daily-combo               — today's combo cards
  POST /api/daily-combo/check         — check & claim combo
  GET  /health                        — health check
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import async_session_factory
from app.models import CardDefinition, Referral, User
from app.services.cards import (
    check_daily_combo,
    get_daily_combo,
    list_cards_with_user_stage,
    list_categories,
    upgrade_user_card,
)
from app.services.game import (
    calculate_offline_earnings,
    get_profile_data,
    process_tap,
    regenerate_stamina,
)

logger = logging.getLogger(__name__)
settings = get_settings()

api_router = APIRouter(prefix="/api", tags=["game"])


# ---------------------------------------------------------------------------
#  Dependency: DB session
# ---------------------------------------------------------------------------

async def get_session():
    async with async_session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
#  Request / Response models
# ---------------------------------------------------------------------------

class TapRequest(BaseModel):
    telegram_id: int
    tap_amount: int = 1


class UpgradeRequest(BaseModel):
    telegram_id: int
    card_id: int


class ComboCheckRequest(BaseModel):
    telegram_id: int


class ApiResponse(BaseModel):
    ok: bool
    message: str = ""
    data: dict | list | None = None


# ---------------------------------------------------------------------------
#  Helper: get user or 404
# ---------------------------------------------------------------------------

async def _get_user(session: AsyncSession, telegram_id: int) -> User:
    user = (
        await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ===========================================================================
#  GET /api/user/{telegram_id} — Profile
# ===========================================================================

@api_router.get("/user/{telegram_id}")
async def get_user_profile(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await _get_user(session, telegram_id)

    # Regenerate stamina
    regenerate_stamina(user)

    # Calculate offline earnings
    offline = calculate_offline_earnings(user)

    await session.commit()

    return ApiResponse(
        ok=True,
        data=get_profile_data(user, offline),
    )


# ===========================================================================
#  POST /api/tap — Tap to earn
# ===========================================================================

@api_router.post("/tap")
async def tap_endpoint(
    req: TapRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await _get_user(session, req.telegram_id)

    success, msg, data = await process_tap(session, user, req.tap_amount)

    if not success:
        return ApiResponse(ok=False, message=msg, data=data)

    return ApiResponse(ok=True, message=msg, data=data)


# ===========================================================================
#  GET /api/categories — Card categories
# ===========================================================================

@api_router.get("/categories")
async def get_categories(
    session: AsyncSession = Depends(get_session),
):
    cats = await list_categories(session)
    return ApiResponse(ok=True, data=cats)


# ===========================================================================
#  GET /api/cards/{telegram_id} — Cards list
# ===========================================================================

@api_router.get("/cards/{telegram_id}")
async def get_cards(
    telegram_id: int,
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    user = await _get_user(session, telegram_id)
    cards = await list_cards_with_user_stage(session, user, category)
    return ApiResponse(ok=True, data=cards)


# ===========================================================================
#  POST /api/cards/upgrade — Upgrade card
# ===========================================================================

@api_router.post("/cards/upgrade")
async def upgrade_card(
    req: UpgradeRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await _get_user(session, req.telegram_id)

    success, msg, data = await upgrade_user_card(session, user, req.card_id)

    if not success:
        return ApiResponse(ok=False, message=msg, data=data)

    return ApiResponse(ok=True, message=msg, data=data)


# ===========================================================================
#  GET /api/leaderboard — Top 50
# ===========================================================================

@api_router.get("/leaderboard")
async def leaderboard(
    session: AsyncSession = Depends(get_session),
):
    top = list(
        (await session.execute(
            select(User)
            .where(User.is_banned.is_(False))
            .order_by(desc(User.total_tokens))
            .limit(50)
        )).scalars().all()
    )

    data = [
        {
            "rank": idx + 1,
            "telegram_id": u.telegram_id,
            "first_name": u.first_name or u.username or f"User#{u.telegram_id}",
            "balance": round(u.total_tokens, 4),
            "profit_per_hour": round(u.profit_per_hour, 4),
            "level": u.level,
            "is_vip": u.is_vip,
        }
        for idx, u in enumerate(top)
    ]

    return ApiResponse(ok=True, data=data)


# ===========================================================================
#  GET /api/referrals/{telegram_id} — Referral info
# ===========================================================================

@api_router.get("/referrals/{telegram_id}")
async def get_referrals(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await _get_user(session, telegram_id)

    # Count referrals
    ref_count = (
        await session.execute(
            select(func.count()).select_from(Referral).where(
                Referral.inviter_id == user.id
            )
        )
    ).scalar() or 0

    # Get invited users
    invited = list(
        (await session.execute(
            select(User).join(
                Referral, Referral.invitee_id == User.id
            ).where(Referral.inviter_id == user.id)
            .order_by(desc(User.created_at))
            .limit(50)
        )).scalars().all()
    )

    friends_list = [
        {
            "first_name": u.first_name or u.username or f"User#{u.telegram_id}",
            "level": u.level,
            "joined": u.created_at.isoformat() if u.created_at else None,
        }
        for u in invited
    ]

    return ApiResponse(
        ok=True,
        data={
            "invite_link": f"https://t.me/vtx_earn_bot?start={user.telegram_id}",
            "total_invited": ref_count,
            "reward_per_friend": settings.referral_reward,
            "friends": friends_list,
        },
    )


# ===========================================================================
#  GET /api/daily-combo — Today's combo
# ===========================================================================

@api_router.get("/daily-combo")
async def daily_combo_info(
    session: AsyncSession = Depends(get_session),
):
    combo = await get_daily_combo(session)
    if not combo:
        return ApiResponse(ok=True, data={"active": False})

    # Get card details for the combo
    card_ids = [combo.card_id_1, combo.card_id_2, combo.card_id_3]
    cards = list(
        (await session.execute(
            select(CardDefinition).where(CardDefinition.id.in_(card_ids))
        )).scalars().all()
    )

    card_data = [
        {
            "card_id": c.id,
            "title": c.title,
            "category": c.category,
            "rarity": c.rarity,
            "image_url": c.image_url,
        }
        for c in cards
    ]

    return ApiResponse(
        ok=True,
        data={
            "active": True,
            "date": combo.date_key,
            "reward": combo.reward_tokens,
            "cards": card_data,
        },
    )


# ===========================================================================
#  POST /api/daily-combo/check — Check & claim combo
# ===========================================================================

@api_router.post("/daily-combo/check")
async def daily_combo_check(
    req: ComboCheckRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await _get_user(session, req.telegram_id)
    success, msg, reward = await check_daily_combo(session, user)
    return ApiResponse(
        ok=success,
        message=msg,
        data={"reward": reward} if success else None,
    )


# ===========================================================================
#  GET /health — Health check
# ===========================================================================

@api_router.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}


# ===========================================================================
#  Admin API — protected by ADMIN_API_TOKEN
# ===========================================================================

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/users/count")
async def admin_user_count(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    if token != settings.admin_api_token:
        raise HTTPException(status_code=403, detail="Forbidden")

    total = (
        await session.execute(select(func.count()).select_from(User))
    ).scalar() or 0

    return {"total_users": total}


@admin_router.get("/users/top")
async def admin_top_users(
    token: str,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    if token != settings.admin_api_token:
        raise HTTPException(status_code=403, detail="Forbidden")

    top = list(
        (await session.execute(
            select(User)
            .order_by(desc(User.total_tokens))
            .limit(min(limit, 100))
        )).scalars().all()
    )

    return {
        "users": [
            {
                "telegram_id": u.telegram_id,
                "username": u.username,
                "balance": u.total_tokens,
                "pph": u.profit_per_hour,
                "level": u.level,
                "banned": u.is_banned,
            }
            for u in top
        ]
    }
