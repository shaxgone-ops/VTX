"""
VTX Earn Arena — Broadcast Service
====================================
Sends periodic messages to all active users.
Respects Telegram rate limits (30 messages/second).
Each user receives the message in their own language.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import BroadcastLog, User
from app.services.i18n import normalize_locale, tr

logger = logging.getLogger(__name__)
settings = get_settings()


async def broadcast_daily(bot: Bot, session: AsyncSession) -> tuple[int, int]:
    """
    Send daily engagement message to all non-banned users.
    Returns (sent_count, failed_count).

    Each user receives the message in their own language,
    with a photo and WebApp button.
    """
    stmt = select(User).where(User.is_banned.is_(False))
    users = list((await session.execute(stmt)).scalars().all())

    sent = 0
    failed = 0
    photo_url = settings.safe_cover_image_url

    for user in users:
        locale = normalize_locale(user.language_code or user.locale)
        text = tr(locale, "daily_ping")
        open_label = tr(locale, "open_app", "Open App")

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"🎮 {open_label}",
                        web_app=WebAppInfo(url=settings.frontend_public_url),
                    )
                ]
            ]
        )

        try:
            await bot.send_photo(
                chat_id=user.telegram_id,
                photo=photo_url,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            sent += 1
        except Exception as exc:
            # Try text-only fallback if photo fails
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=kb,
                )
                sent += 1
            except Exception:
                failed += 1
                logger.debug(
                    "Broadcast failed for user %d: %s",
                    user.telegram_id,
                    exc,
                )

        # Respect Telegram rate limit: 30 msg/sec → ~33ms per message
        await asyncio.sleep(0.04)

    # Log the broadcast
    log_entry = BroadcastLog(
        message_key="daily_ping",
        sent_count=sent,
        failed_count=failed,
    )
    session.add(log_entry)
    await session.commit()

    logger.info("Broadcast complete: sent=%d, failed=%d", sent, failed)
    return sent, failed


async def broadcast_loop(bot: Bot, session_factory) -> None:
    """
    Background task that sends broadcast every N hours.
    Runs forever until the application shuts down.
    """
    interval_seconds = settings.broadcast_interval_hours * 3600

    while True:
        try:
            await asyncio.sleep(interval_seconds)
            async with session_factory() as session:
                await broadcast_daily(bot, session)
        except asyncio.CancelledError:
            logger.info("Broadcast loop cancelled")
            break
        except Exception as exc:
            logger.error("Broadcast loop error: %s", exc, exc_info=True)
            await asyncio.sleep(60)  # Wait a minute before retrying
