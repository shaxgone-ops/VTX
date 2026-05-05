import asyncio

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from sqlalchemy import select

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models import BroadcastLog, User
from app.services.i18n import tr

settings = get_settings()


async def broadcast_daily(bot: Bot) -> None:
    sent = 0
    failed = 0
    async with AsyncSessionLocal() as session:
        users = list((await session.execute(select(User).where(User.is_banned.is_(False)))).scalars().all())
        for user in users:
            text = tr(user.locale, "daily_ping", "Daily update is live")
            button_text = tr(user.locale, "open_app", "Open App")
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=button_text, web_app=WebAppInfo(url=settings.frontend_public_url))]
                ]
            )
            try:
                await bot.send_photo(chat_id=user.telegram_id, photo=settings.cover_image_url, caption=text, reply_markup=kb)
                sent += 1
            except Exception:
                failed += 1
        session.add(BroadcastLog(message_key="daily_ping", sent_count=sent, failed_count=failed))
        await session.commit()


async def broadcast_loop(bot: Bot) -> None:
    while True:
        await broadcast_daily(bot)
        await asyncio.sleep(max(1, settings.broadcast_interval_hours) * 3600)
