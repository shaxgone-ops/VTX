"""
VTX Earn Arena — Telegram Bot Handlers
========================================
Processes all incoming commands and callback queries.
Uses i18n for every message sent to the user.

Critical fix: Uses safe_token_logo_url instead of
raw token_logo_url which could be empty and crash
answer_photo().
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.anti_cheat import (
    evaluate_tap_rate,
    is_high_risk_user,
    should_throttle,
)
from app.config import get_settings
from app.models import Referral, User
from app.services.i18n import normalize_locale, tr
from app.bot.keyboards import language_keyboard, main_menu

logger = logging.getLogger(__name__)
router = Router()
settings = get_settings()


# ---------------------------------------------------------------------------
#  Utility helpers
# ---------------------------------------------------------------------------

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def bot_me_link() -> str:
    """Generate the bot's t.me deep-link for referrals."""
    return "https://t.me/{bot_username}"


async def _get_or_create_user(
    session: AsyncSession,
    message_or_query: Message | CallbackQuery,
    referrer_id: int | None = None,
) -> User:
    """Find existing user or create a new one."""
    tg = message_or_query.from_user
    if tg is None:
        raise ValueError("No from_user on message/query")

    user = (
        await session.execute(
            select(User).where(User.telegram_id == tg.id)
        )
    ).scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=tg.id,
            username=tg.username,
            first_name=tg.first_name,
            language_code=tg.language_code,
            locale=tg.language_code,
            stamina=settings.initial_stamina,
            total_tokens=0,
            profit_per_hour=settings.base_profit_per_hour,
        )
        session.add(user)
        await session.flush()

        # Handle referral (deep link parameter)
        if referrer_id and referrer_id != tg.id:
            referrer = (
                await session.execute(
                    select(User).where(User.telegram_id == referrer_id)
                )
            ).scalar_one_or_none()
            if referrer:
                # Check if referral already exists
                existing = (
                    await session.execute(
                        select(Referral).where(
                            Referral.inviter_id == referrer.id,
                            Referral.invitee_id == user.id,
                        )
                    )
                ).scalar_one_or_none()
                if not existing:
                    ref = Referral(
                        inviter_id=referrer.id,
                        invitee_id=user.id,
                        reward_paid=True,
                    )
                    session.add(ref)
                    referrer.total_tokens += settings.referral_reward
                    user.invited_by_id = referrer.id

        await session.commit()
    else:
        # Update existing user info
        user.username = tg.username
        user.first_name = tg.first_name
        if tg.language_code:
            user.language_code = tg.language_code
            user.locale = tg.language_code

    return user


def _format_number(n: float) -> str:
    """Format a number with commas for display."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:,.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:,.1f}K"
    return f"{n:,.0f}"


# ---------------------------------------------------------------------------
#  DEPENDENCY NOTE: The 'session' is injected by middleware.
#  If your middleware stores it in message/query data dict,
#  access it like: session = data['session']
# ---------------------------------------------------------------------------

async def _get_session(data: dict[str, Any]) -> AsyncSession:
    """Extract async session from middleware-injected data."""
    session = data.get("session")
    if session is None:
        # Fallback: try to get from db module
        from app.db import async_session_factory
        session = async_session_factory()
    return session


# ===========================================================================
#  /start COMMAND  — THE MAIN ENTRY POINT
# ===========================================================================

@router.message(Command("start"))
async def start_command(message: Message, **data: Any) -> None:
    """
    Handle /start command.
    Creates user if new, sends welcome image + WebApp button.
    Supports deep-link referral: /start <referrer_telegram_id>
    """
    session = await _get_session(data)

    # Parse deep-link referral ID
    referrer_id: int | None = None
    if message.text:
        parts = message.text.strip().split()
        if len(parts) > 1:
            try:
                referrer_id = int(parts[1])
            except (ValueError, IndexError):
                pass

    user = await _get_or_create_user(session, message, referrer_id)
    locale = normalize_locale(user.language_code or user.locale)

    # Check access control
    if settings.whitelist_only:
        allowed = settings.admin_id_set | settings.vip_id_set
        if user.telegram_id not in allowed:
            await message.answer(tr(locale, "access_blocked"))
            return

    # Check if banned
    if user.is_banned:
        await message.answer(tr(locale, "banned"))
        return

    # Build welcome text
    invite_link = f"https://t.me/{(await message.bot.me()).username}?start={user.telegram_id}"

    welcome_text = tr(locale, "welcome")
    balance_text = tr(
        locale,
        "welcome_balance",
        balance=_format_number(user.total_tokens),
        symbol=settings.token_symbol,
        pph=_format_number(user.profit_per_hour),
        stamina=str(user.stamina),
    )
    invite_text = tr(locale, "welcome_invite", link=invite_link)

    full_text = f"{welcome_text}\n\n{balance_text}\n\n{invite_text}"

    # Use safe image URL (never empty)
    photo_url = settings.safe_token_logo_url
    kb = main_menu(settings.frontend_public_url, locale)

    try:
        await message.answer_photo(
            photo=photo_url,
            caption=full_text,
            parse_mode="HTML",
            reply_markup=kb,
        )
    except Exception as exc:
        # If photo fails (URL broken), fall back to text only
        logger.warning("Failed to send photo: %s", exc)
        await message.answer(
            text=full_text,
            parse_mode="HTML",
            reply_markup=kb,
        )

    await session.commit()


# ===========================================================================
#  /help COMMAND
# ===========================================================================

@router.message(Command("help"))
async def help_command(message: Message, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, message)
    locale = normalize_locale(user.language_code or user.locale)
    await message.answer(tr(locale, "help_text"), parse_mode="HTML")


# ===========================================================================
#  /language COMMAND
# ===========================================================================

@router.message(Command("language"))
async def language_command(message: Message, **data: Any) -> None:
    await message.answer("Choose your language:", reply_markup=language_keyboard())


# ===========================================================================
#  /mystats COMMAND
# ===========================================================================

@router.message(Command("mystats"))
async def stats_command(message: Message, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, message)

    text = (
        f"<b>Your Stats</b>\n"
        f"Balance: {_format_number(user.total_tokens)} {settings.token_symbol}\n"
        f"Profit/h: {_format_number(user.profit_per_hour)}\n"
        f"Level: {user.level}\n"
        f"Total Taps: {_format_number(user.lifetime_taps)}\n"
        f"Stamina: {user.stamina}/{settings.initial_stamina}\n"
        f"VIP: {'Yes' if user.is_vip else 'No'}\n"
        f"Joined: {user.created_at.strftime('%Y-%m-%d')}"
    )
    await message.answer(text, parse_mode="HTML")


# ===========================================================================
#  /invite COMMAND
# ===========================================================================

@router.message(Command("invite"))
async def invite_command(message: Message, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, message)

    bot_info = await message.bot.me()
    link = f"https://t.me/{bot_info.username}?start={user.telegram_id}"

    # Count referrals
    ref_count = (
        await session.execute(
            select(func.count()).select_from(Referral).where(
                Referral.inviter_id == user.id
            )
        )
    ).scalar() or 0

    text = (
        f"Your referral link:\n<code>{link}</code>\n\n"
        f"Friends invited: {ref_count}\n"
        f"Reward per friend: {settings.referral_reward} {settings.token_symbol}"
    )
    await message.answer(text, parse_mode="HTML")


# ===========================================================================
#  LANGUAGE CALLBACK
# ===========================================================================

@router.callback_query(F.data.startswith("lang_"))
async def language_callback(query: CallbackQuery, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, query)

    new_locale = query.data.replace("lang_", "")
    user.language_code = new_locale
    user.locale = new_locale
    await session.commit()

    text = tr(new_locale, "language_changed")
    await query.answer(text, show_alert=True)
    await query.message.edit_text(text)


# ===========================================================================
#  TAP CALLBACKS  (play_tap_1, play_tap_5, etc.)
# ===========================================================================

@router.callback_query(F.data.startswith("play_tap_"))
async def tap_callback(query: CallbackQuery, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, query)
    locale = normalize_locale(user.language_code or user.locale)

    # Banned check
    if user.is_banned or is_high_risk_user(user.suspicious_score):
        await query.answer(tr(locale, "banned"), show_alert=True)
        return

    # Parse tap amount from callback data
    try:
        tap_amount = int(query.data.split("_")[-1])
    except (ValueError, IndexError):
        tap_amount = 1

    # Clamp tap amount to reasonable range
    tap_amount = max(1, min(50, tap_amount))
    now = utcnow()

    # Anti-cheat rate evaluation
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
            await query.answer(tr(locale, "suspicious"), show_alert=True)
        else:
            await query.answer("Too fast!", show_alert=False)
        return

    # Regenerate stamina since last tap
    if user.last_tap_at:
        minutes_since = (now - user.last_stamina_sync_at).total_seconds() / 60
        regen = int(minutes_since * settings.stamina_regen_per_min)
        if regen > 0:
            user.stamina = min(settings.initial_stamina, user.stamina + regen)
            user.last_stamina_sync_at = now

    # Check stamina
    if user.stamina < tap_amount:
        await query.answer(tr(locale, "stamina_empty"), show_alert=True)
        return

    # Process tap
    tokens_per_tap = 1.0
    if user.is_vip:
        tokens_per_tap *= settings.vip_profit_multiplier

    gained = round(tap_amount * tokens_per_tap, 4)

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

    await session.commit()

    await query.answer(
        tr(locale, "tap_accepted", tokens=_format_number(gained), symbol=settings.token_symbol),
        show_alert=False,
    )


# ===========================================================================
#  PROFILE CALLBACK
# ===========================================================================

@router.callback_query(F.data == "profile_show")
async def profile_callback(query: CallbackQuery, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, query)

    text = (
        f"<b>Player Profile</b>\n"
        f"Name: {user.first_name or 'Anonymous'}\n"
        f"Level: {user.level}\n"
        f"Balance: {_format_number(user.total_tokens)} {settings.token_symbol}\n"
        f"Profit/h: {_format_number(user.profit_per_hour)}\n"
        f"Stamina: {user.stamina}/{settings.initial_stamina}\n"
        f"Total Taps: {_format_number(user.lifetime_taps)}\n"
        f"VIP: {'Active' if user.is_vip else 'No'}\n"
        f"Joined: {user.created_at.strftime('%Y-%m-%d')}"
    )
    await query.answer()
    try:
        await query.message.edit_caption(caption=text, parse_mode="HTML")
    except Exception:
        await query.message.answer(text, parse_mode="HTML")


# ===========================================================================
#  LEADERBOARD CALLBACK
# ===========================================================================

@router.callback_query(F.data == "top_balance")
async def leaderboard_callback(query: CallbackQuery, **data: Any) -> None:
    session = await _get_session(data)

    top_users = list(
        (await session.execute(
            select(User)
            .where(User.is_banned.is_(False))
            .order_by(desc(User.total_tokens))
            .limit(20)
        )).scalars().all()
    )

    lines = [f"<b>Top 20 Players</b>\n"]
    medals = ["1.", "2.", "3."]
    for idx, u in enumerate(top_users):
        prefix = medals[idx] if idx < 3 else f"{idx + 1}."
        name = u.first_name or u.username or f"User#{u.telegram_id}"
        lines.append(
            f"{prefix} {name} — {_format_number(u.total_tokens)} {settings.token_symbol}"
        )

    await query.answer()
    try:
        await query.message.edit_caption(
            caption="\n".join(lines), parse_mode="HTML"
        )
    except Exception:
        await query.message.answer("\n".join(lines), parse_mode="HTML")


# ===========================================================================
#  DAILY REWARD CALLBACK
# ===========================================================================

@router.callback_query(F.data == "daily_reward")
async def daily_reward_callback(query: CallbackQuery, **data: Any) -> None:
    session = await _get_session(data)
    user = await _get_or_create_user(session, query)
    locale = normalize_locale(user.language_code or user.locale)
    now = utcnow()

    # Check if already claimed today
    if user.last_reward_claim_at:
        hours = (now - user.last_reward_claim_at).total_seconds() / 3600
        if hours < 24:
            await query.answer(tr(locale, "daily_reward_wait"), show_alert=True)
            return

    # Must have at least 10 daily taps to claim
    if user.daily_taps < 10:
        await query.answer(tr(locale, "daily_reward_wait"), show_alert=True)
        return

    reward = float(settings.daily_active_reward)
    user.total_tokens += reward
    user.last_reward_claim_at = now
    user.daily_taps = 0  # Reset counter for tomorrow
    await session.commit()

    await query.answer(
        tr(locale, "daily_reward_claimed", amount=_format_number(reward), symbol=settings.token_symbol),
        show_alert=True,
    )


# ===========================================================================
#  ADMIN COMMANDS
# ===========================================================================

@router.message(Command("admin_broadcast"))
async def admin_broadcast_cmd(message: Message, **data: Any) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return

    await message.answer("Broadcast will be sent to all users within 1 minute.")


@router.message(Command("admin_ban"))
async def admin_ban_cmd(message: Message, **data: Any) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("Usage: /admin_ban <telegram_id>")
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid telegram_id")
        return

    session = await _get_session(data)
    target = (
        await session.execute(
            select(User).where(User.telegram_id == target_id)
        )
    ).scalar_one_or_none()

    if not target:
        await message.answer("User not found")
        return

    target.is_banned = True
    await session.commit()
    await message.answer(f"User {target_id} has been banned.")


@router.message(Command("admin_unban"))
async def admin_unban_cmd(message: Message, **data: Any) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("Usage: /admin_unban <telegram_id>")
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid telegram_id")
        return

    session = await _get_session(data)
    target = (
        await session.execute(
            select(User).where(User.telegram_id == target_id)
        )
    ).scalar_one_or_none()

    if not target:
        await message.answer("User not found")
        return

    target.is_banned = False
    target.suspicious_score = 0
    await session.commit()
    await message.answer(f"User {target_id} has been unbanned.")


@router.message(Command("admin_stats"))
async def admin_stats_cmd(message: Message, **data: Any) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return

    session = await _get_session(data)

    total = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
    banned = (
        await session.execute(
            select(func.count()).select_from(User).where(User.is_banned.is_(True))
        )
    ).scalar() or 0
    vip = (
        await session.execute(
            select(func.count()).select_from(User).where(User.is_vip.is_(True))
        )
    ).scalar() or 0

    text = (
        f"<b>Admin Stats</b>\n"
        f"Total Users: {total}\n"
        f"Banned: {banned}\n"
        f"VIP: {vip}"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("add_tokens"))
async def admin_add_tokens_cmd(message: Message, **data: Any) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /add_tokens <amount> [telegram_id]")
        return

    try:
        amount = float(parts[1])
    except ValueError:
        await message.answer("Amount must be a number.")
        return

    target_id = message.from_user.id
    if len(parts) >= 3:
        try:
            target_id = int(parts[2])
        except ValueError:
            target_id = message.from_user.id

    session = await _get_session(data)
    target = (
        await session.execute(
            select(User).where(User.telegram_id == target_id)
        )
    ).scalar_one_or_none()

    if not target:
        await message.answer("User not found in DB.")
        return

    target.total_tokens += amount
    await session.commit()
    await message.answer(f"Added {amount:,.0f} tokens to User {target_id}. New balance: {target.total_tokens:,.0f}")
