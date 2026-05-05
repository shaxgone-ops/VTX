from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def main_menu(frontend_public_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Play x1", callback_data="play_tap_1"),
                InlineKeyboardButton(text="Play x5", callback_data="play_tap_5"),
                InlineKeyboardButton(text="Play x10", callback_data="play_tap_10"),
            ],
            [
                InlineKeyboardButton(text="Play x25", callback_data="play_tap_25"),
                InlineKeyboardButton(text="Play x50", callback_data="play_tap_50"),
            ],
            [
                InlineKeyboardButton(text="My Stats", callback_data="profile_show"),
                InlineKeyboardButton(text="Top", callback_data="top_balance"),
            ],
            [
                InlineKeyboardButton(text="Daily Reward", callback_data="daily_reward"),
                InlineKeyboardButton(text="Quest Board", callback_data="quest_board"),
            ],
            [
                InlineKeyboardButton(text="Claim Q1", callback_data="quest_claim_tap_500"),
                InlineKeyboardButton(text="Claim Q2", callback_data="quest_claim_tap_5000"),
            ],
            [
                InlineKeyboardButton(text="Boost 100", callback_data="boost_pph_100"),
                InlineKeyboardButton(text="Boost 500", callback_data="boost_pph_500"),
            ],
            [
                InlineKeyboardButton(text="Market Sell 50", callback_data="market_sell_50"),
                InlineKeyboardButton(text="Market Sell 250", callback_data="market_sell_250"),
            ],
            [
                InlineKeyboardButton(text="Withdraw 100", callback_data="withdraw_100"),
            ],
            [
                InlineKeyboardButton(text="Open Web App", web_app=WebAppInfo(url=frontend_public_url)),
            ],
        ]
    )
