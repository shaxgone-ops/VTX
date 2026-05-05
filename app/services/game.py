from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.anti_cheat import evaluate_tap_rate, is_high_risk_user
from app.config import get_settings
from app.models import TapEvent, User
from app.services.users import apply_stamina_regen

settings = get_settings()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def tap_to_gain(user: User, tap_amount: int) -> float:
    base_gain = tap_amount * 0.7
    vip_multiplier = settings.vip_profit_multiplier if user.is_vip else 1.0
    pph_factor = max(1.0, user.profit_per_hour / max(1, settings.base_profit_per_hour))
    return round(base_gain * vip_multiplier * (pph_factor ** 0.25), 6)


async def process_tap(session: AsyncSession, user: User, tap_amount: int) -> dict:
    apply_stamina_regen(user)
    now = now_utc()
    is_valid, penalty = evaluate_tap_rate(user.last_tap_at, now, tap_amount)
    if not is_valid:
        user.suspicious_score += penalty
        if is_high_risk_user(user.suspicious_score):
            user.is_banned = True
        await session.commit()
        return {
            "ok": False,
            "reason": "anti_cheat",
            "suspicious_score": user.suspicious_score,
            "is_banned": user.is_banned,
        }
    if user.is_banned:
        return {"ok": False, "reason": "banned"}
    if user.stamina <= 0:
        return {"ok": False, "reason": "stamina_empty"}
    tap_cost = min(user.stamina, tap_amount)
    user.stamina -= tap_cost
    gain = tap_to_gain(user, tap_cost)
    user.total_tokens += gain
    user.lifetime_taps += tap_cost
    user.daily_taps += tap_cost
    user.last_tap_at = now
    user.tap_combo_counter += 1
    if user.tap_combo_counter % 200 == 0:
        user.level += 1
        user.profit_per_hour += 55
    event = TapEvent(user_id=user.id, tap_amount=tap_cost, gain_tokens=gain)
    session.add(event)
    await session.commit()
    return {
        "ok": True,
        "spent_stamina": tap_cost,
        "gain_tokens": gain,
        "stamina_left": user.stamina,
        "total_tokens": user.total_tokens,
        "combo": user.tap_combo_counter,
    }
