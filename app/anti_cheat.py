from datetime import datetime, timezone

from app.config import get_settings

settings = get_settings()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def evaluate_tap_rate(last_tap_at: datetime | None, now: datetime, tap_amount: int) -> tuple[bool, int]:
    if tap_amount <= 0:
        return False, 8
    if tap_amount > settings.max_tap_per_second * 3:
        return False, 10
    if not last_tap_at:
        return True, 0
    delta = (now - last_tap_at).total_seconds()
    if delta <= 0:
        return False, 12
    rate = tap_amount / delta
    if rate > settings.max_tap_per_second:
        penalty = min(20, int(rate))
        return False, penalty
    return True, 0


def is_high_risk_user(score: int) -> bool:
    return score >= 100
