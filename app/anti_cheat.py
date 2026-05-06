"""
VTX Earn Arena — Anti-Cheat Engine
====================================
Multi-layer detection for auto-clickers and abuse:

1. Rate limiting:  max N taps per second
2. Pattern analysis:  too-even intervals = bot
3. Burst detection:  rapid fire after idle = suspicious
4. Progressive penalty:  suspicious_score accumulates
5. Auto-ban threshold:  score >= 100 → account locked
"""

from __future__ import annotations

import statistics
from collections import deque
from datetime import datetime, timezone

from app.config import get_settings

settings = get_settings()

# In-memory ring buffer for per-user tap timestamps (not persisted)
# key = user_id, value = deque of recent tap timestamps
_tap_history: dict[int, deque[float]] = {}
_HISTORY_SIZE = 30  # Keep last 30 tap events for pattern analysis


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _record_tap_time(user_id: int) -> None:
    """Record current timestamp in the per-user ring buffer."""
    now = utc_now().timestamp()
    if user_id not in _tap_history:
        _tap_history[user_id] = deque(maxlen=_HISTORY_SIZE)
    _tap_history[user_id].append(now)


def _detect_bot_pattern(user_id: int) -> tuple[bool, str]:
    """
    Analyze tap interval distribution.
    Auto-clickers produce very consistent intervals (low std deviation).
    Real humans have irregular, noisy intervals.

    Returns (is_suspicious, reason).
    """
    history = _tap_history.get(user_id)
    if not history or len(history) < 10:
        return False, ""

    # Calculate intervals between consecutive taps
    timestamps = list(history)
    intervals: list[float] = []
    for i in range(1, len(timestamps)):
        delta = timestamps[i] - timestamps[i - 1]
        if 0 < delta < 60:  # Only consider recent rapid taps
            intervals.append(delta)

    if len(intervals) < 8:
        return False, ""

    # Coefficient of variation: std / mean
    # Bots: CV < 0.1 (very consistent)
    # Humans: CV > 0.2 (natural variation)
    mean_interval = statistics.mean(intervals)
    if mean_interval <= 0:
        return True, "zero_mean_interval"

    std_interval = statistics.stdev(intervals)
    cv = std_interval / mean_interval

    if cv < 0.05:
        # Almost perfectly regular — definitely a bot
        return True, "perfect_regularity"

    if cv < 0.10:
        # Very regular — likely scripted
        return True, "low_variance_tapping"

    return False, ""


def _detect_burst(
    last_tap_at: datetime | None,
    now: datetime,
    tap_amount: int,
) -> tuple[bool, str]:
    """
    Detect suspicious burst: user was idle for a while,
    then suddenly sends a huge amount of taps.
    """
    if not last_tap_at:
        return False, ""

    delta_seconds = (now - last_tap_at).total_seconds()

    # If more than 5 minutes idle, then sends >20 taps at once
    if delta_seconds > 300 and tap_amount > 20:
        return True, "burst_after_idle"

    return False, ""


def evaluate_tap_rate(
    last_tap_at: datetime | None,
    now: datetime,
    tap_amount: int,
    user_id: int = 0,
) -> tuple[bool, int]:
    """
    Evaluate whether a tap event is legitimate.

    Returns (is_valid, penalty_points).
    If is_valid is False, caller should add penalty_points
    to the user's suspicious_score.
    """
    # Negative or zero taps are always invalid
    if tap_amount <= 0:
        return False, 8

    # Absurdly large single tap (>3× the max taps per second)
    if tap_amount > settings.max_tap_per_second * 3:
        return False, 10

    # Record this tap for pattern analysis
    if user_id > 0:
        _record_tap_time(user_id)

    # Check time-based rate
    if last_tap_at:
        delta = (now - last_tap_at).total_seconds()

        # Identical or backward timestamps
        if delta <= 0:
            return False, 12

        # Calculate taps per second
        rate = tap_amount / max(0.01, delta)

        if rate > settings.max_tap_per_second:
            # Penalty scales with how much over the limit
            penalty = min(20, int(rate * 1.5))
            return False, penalty

    # Check burst pattern
    burst_suspicious, burst_reason = _detect_burst(last_tap_at, now, tap_amount)
    if burst_suspicious:
        return False, 6

    # Check bot-like pattern (only if we have history)
    if user_id > 0:
        bot_suspicious, bot_reason = _detect_bot_pattern(user_id)
        if bot_suspicious:
            return False, 15  # Heavy penalty for confirmed bot pattern

    return True, 0


def is_high_risk_user(score: int) -> bool:
    """Auto-ban threshold: score >= 100."""
    return score >= 100


def should_throttle(score: int) -> bool:
    """Warn threshold: score >= 50 but not yet banned."""
    return 50 <= score < 100


def decay_suspicious_score(current_score: int, hours_since_last_flag: float) -> int:
    """
    Gradually reduce suspicious score over time if user behaves normally.
    Decays 1 point per hour, minimum 0.
    """
    if current_score <= 0:
        return 0
    decay = int(hours_since_last_flag)
    return max(0, current_score - decay)
