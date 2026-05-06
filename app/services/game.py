"""
VTX Earn Arena — Game Service
==============================
Core gameplay logic:
  - Tap processing (stamina, anti-cheat)
  - Offline PPH earnings calculation
  - Stamina regeneration
  - Level progression
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.anti_cheat import (
    evaluate_tap_rate,
    is_high_risk_user,
    should_throttle,
)
from app.config import get_settings
from app.models import TapEvent, User

logger = logging.getLogger(__name__)
settings = get_settings()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
#  Stamina regeneration
# ---------------------------------------------------------------------------

def regenerate_stamina(user: User) -> int:
    """
    Calculate stamina regenerated since last sync.
    Updates user.stamina and user.last_stamina_sync_at.
    Returns amount regenerated.
    """
    now = utcnow()
    elapsed_minutes = (now - user.last_stamina_sync_at).total_seconds() / 60.0

    if elapsed_minutes < 0.1:
        return 0

    regen = int(elapsed_minutes * settings.stamina_regen_per_min)
    if regen <= 0:
        return 0

    old_stamina = user.stamina
    user.stamina = min(settings.initial_stamina, user.stamina + regen)
    user.last_stamina_sync_at = now

    return user.stamina - old_stamina


# ---------------------------------------------------------------------------
#  Offline PPH earnings
# ---------------------------------------------------------------------------

def calculate_offline_earnings(user: User) -> float:
    """
    Calculate tokens earned while user was offline based on PPH.
    Caps at 3 hours of offline earnings to prevent abuse.
    Updates user.last_earnings_sync_at.
    Returns tokens earned.
    """
    now = utcnow()
    elapsed_hours = (now - user.last_earnings_sync_at).total_seconds() / 3600.0

    if elapsed_hours < 0.01:  # Less than 36 seconds
        return 0.0

    # Cap offline earnings at 3 hours
    capped_hours = min(3.0, elapsed_hours)
    tokens = user.profit_per_hour * capped_hours

    if user.is_vip:
        tokens *= settings.vip_profit_multiplier

    tokens = round(tokens, 4)

    if tokens > 0:
        user.total_tokens += tokens
        user.last_earnings_sync_at = now

    return tokens


# ---------------------------------------------------------------------------
#  Process a tap (HTTP API version)
# ---------------------------------------------------------------------------

async def process_tap(
    session: AsyncSession,
    user: User,
    tap_amount: int,
) -> tuple[bool, str, dict | None]:
    """
    Process a tap event from the Mini App API.
    Returns (success, message, data_dict).

    Handles:
      1. Ban/suspicious check
      2. Anti-cheat rate limiting
      3. Stamina check & consumption
      4. Token gain calculation
      5. Level progression
    """
    now = utcnow()

    # ── 1. Ban check ──────────────────────────────────────────────────────
    if user.is_banned or is_high_risk_user(user.suspicious_score):
        return False, "Account suspended", None

    # ── 2. Validate tap amount ────────────────────────────────────────────
    tap_amount = max(1, min(100, tap_amount))

    # ── 3. Anti-cheat evaluation ──────────────────────────────────────────
    is_valid, penalty = evaluate_tap_rate(
        last_tap_at=user.last_tap_at,
        now=now,
        tap_amount=tap_amount,
        user_id=user.telegram_id,
    )

    if not is_valid:
        user.suspicious_score += penalty
        await session.commit()
        if should_throttle(user.suspicious_score):
            return False, "Suspicious activity detected", None
        return False, "Too fast, slow down", None

    # ── 4. Regenerate stamina ─────────────────────────────────────────────
    regenerate_stamina(user)

    # ── 5. Stamina check ──────────────────────────────────────────────────
    if user.stamina < tap_amount:
        return False, "Stamina depleted", {
            "stamina": user.stamina,
            "max_stamina": settings.initial_stamina,
            "regen_rate": settings.stamina_regen_per_min,
        }

    # ── 6. Calculate gains ────────────────────────────────────────────────
    tokens_per_tap = 1.0
    if user.is_vip:
        tokens_per_tap *= settings.vip_profit_multiplier

    gained = round(tap_amount * tokens_per_tap, 4)

    # ── 7. Update user state ──────────────────────────────────────────────
    user.stamina -= tap_amount
    user.total_tokens += gained
    user.last_tap_at = now
    user.lifetime_taps += tap_amount
    user.daily_taps += tap_amount
    user.tap_combo_counter += tap_amount

    # Level up every 10,000 lifetime taps
    new_level = (user.lifetime_taps // 10_000) + 1
    if new_level > user.level:
        user.level = new_level

    # ── 8. Log tap event ──────────────────────────────────────────────────
    event = TapEvent(
        user_id=user.id,
        tap_amount=tap_amount,
        gain_tokens=gained,
    )
    session.add(event)
    await session.commit()

    return True, "OK", {
        "gained": gained,
        "balance": round(user.total_tokens, 4),
        "stamina": user.stamina,
        "max_stamina": settings.initial_stamina,
        "lifetime_taps": user.lifetime_taps,
        "level": user.level,
        "profit_per_hour": round(user.profit_per_hour, 4),
        "tap_combo": user.tap_combo_counter,
    }


# ---------------------------------------------------------------------------
#  Get full user profile data for API
# ---------------------------------------------------------------------------

def get_profile_data(user: User, offline_earned: float = 0) -> dict:
    """Build the full profile dict for API responses."""
    return {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "level": user.level,
        "balance": round(user.total_tokens, 4),
        "profit_per_hour": round(user.profit_per_hour, 4),
        "stamina": user.stamina,
        "max_stamina": settings.initial_stamina,
        "lifetime_taps": user.lifetime_taps,
        "daily_taps": user.daily_taps,
        "is_vip": user.is_vip,
        "is_banned": user.is_banned,
        "language_code": user.language_code,
        "offline_earned": round(offline_earned, 4),
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
