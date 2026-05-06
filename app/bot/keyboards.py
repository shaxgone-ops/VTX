"""
VTX Earn Arena — Telegram Keyboards
=====================================
Inline keyboard builders for bot interactions.
All button labels are internationalized.
"""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

from app.services.i18n import tr


def main_menu(
    frontend_url: str,
    locale: str | None = None,
) -> InlineKeyboardMarkup:
    """Primary menu shown after /start with WebApp button."""
    play_label = tr(locale, "play", "Play")
    open_label = tr(locale, "open_app", "Open App")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Tap buttons
            [
                InlineKeyboardButton(text=f"{play_label} x1", callback_data="play_tap_1"),
                InlineKeyboardButton(text=f"{play_label} x5", callback_data="play_tap_5"),
                InlineKeyboardButton(text=f"{play_label} x10", callback_data="play_tap_10"),
            ],
            [
                InlineKeyboardButton(text=f"{play_label} x25", callback_data="play_tap_25"),
                InlineKeyboardButton(text=f"{play_label} x50", callback_data="play_tap_50"),
            ],
            # Info buttons
            [
                InlineKeyboardButton(text=tr(locale, "profile", "Profile"), callback_data="profile_show"),
                InlineKeyboardButton(text=tr(locale, "leaderboard_title", "Top"), callback_data="top_balance"),
            ],
            # Daily & quests
            [
                InlineKeyboardButton(text=tr(locale, "earn", "Earn"), callback_data="daily_reward"),
                InlineKeyboardButton(text="Quest Board", callback_data="quest_board"),
            ],
            # WebApp — main entry to Mini App
            [
                InlineKeyboardButton(
                    text=f"🎮 {open_label}",
                    web_app=WebAppInfo(url=frontend_url),
                ),
            ],
        ]
    )


def language_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for language selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            ],
            [
                InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
                InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de"),
                InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr"),
            ],
            [
                InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es"),
                InlineKeyboardButton(text="🇵🇹 Português", callback_data="lang_pt"),
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
            ],
            [
                InlineKeyboardButton(text="🇮🇳 हिंदी", callback_data="lang_hi"),
                InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh"),
                InlineKeyboardButton(text="🇯🇵 日本語", callback_data="lang_ja"),
            ],
            [
                InlineKeyboardButton(text="🇰🇷 한국어", callback_data="lang_ko"),
                InlineKeyboardButton(text="🇮🇩 Indonesia", callback_data="lang_id"),
                InlineKeyboardButton(text="🇻🇳 Tiếng Việt", callback_data="lang_vi"),
            ],
        ]
    )
