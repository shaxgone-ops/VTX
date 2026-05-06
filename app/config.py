"""
VTX Earn Arena — Application Configuration
============================================
Reads environment variables via pydantic-settings.
Every field that can be empty has a sensible default
so the bot never crashes due to missing env values.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Fallback image URLs — used when ENV values are blank.
# These are royalty-free Unsplash images that always resolve.
# ---------------------------------------------------------------------------
_FALLBACK_TOKEN_LOGO = (
    "https://images.unsplash.com/photo-1621416894569-0f39ed31d247"
    "?auto=format&fit=crop&w=400&q=80"
)
_FALLBACK_COVER = (
    "https://images.unsplash.com/photo-1639762681485-074b7f938ba0"
    "?auto=format&fit=crop&w=800&q=80"
)
_FALLBACK_VIP = (
    "https://images.unsplash.com/photo-1533903345306-15d1c30952de"
    "?auto=format&fit=crop&w=400&q=80"
)
_FALLBACK_MARKET = (
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3"
    "?auto=format&fit=crop&w=800&q=80"
)
_FALLBACK_QUEST = (
    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23"
    "?auto=format&fit=crop&w=800&q=80"
)


class Settings(BaseSettings):
    """Central configuration loaded from .env or system environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Core ──────────────────────────────────────────────────────────────
    app_name: str = Field(default="VTX Earn Arena", alias="APP_NAME")
    environment: Literal["development", "production"] = Field(
        default="production", alias="ENVIRONMENT"
    )

    # ── Telegram Bot ──────────────────────────────────────────────────────
    bot_token: str = Field(alias="BOT_TOKEN")
    webhook_base_url: str = Field(alias="WEBHOOK_BASE_URL")
    webhook_path: str = Field(default="/telegram/webhook", alias="WEBHOOK_PATH")
    webhook_secret: str = Field(default="change_me", alias="WEBHOOK_SECRET")

    # ── Database ──────────────────────────────────────────────────────────
    postgres_dsn: str = Field(alias="POSTGRES_DSN")

    # ── Access Control ────────────────────────────────────────────────────
    admin_ids: str = Field(default="", alias="ADMIN_IDS")
    vip_ids: str = Field(default="", alias="VIP_IDS")
    whitelist_only: bool = Field(default=False, alias="WHITELIST_ONLY")

    # ── Token Branding ────────────────────────────────────────────────────
    token_symbol: str = Field(default="VTX", alias="TOKEN_SYMBOL")
    token_name: str = Field(default="VTX Coin", alias="TOKEN_NAME")

    # ── Image URLs (with fallbacks so bot never crashes) ──────────────────
    token_logo_url: str = Field(default="", alias="TOKEN_LOGO_URL")
    cover_image_url: str = Field(default="", alias="COVER_IMAGE_URL")
    vip_image_url: str = Field(default="", alias="VIP_IMAGE_URL")
    market_image_url: str = Field(default="", alias="MARKET_IMAGE_URL")
    quest_image_url: str = Field(default="", alias="QUEST_IMAGE_URL")

    # ── Public URLs ───────────────────────────────────────────────────────
    frontend_public_url: str = Field(
        default="https://vtx-frontent.onrender.com", alias="FRONTEND_PUBLIC_URL"
    )
    backend_public_url: str = Field(
        default="https://vtx-px5f.onrender.com", alias="BACKEND_PUBLIC_URL"
    )

    # ── Broadcast ─────────────────────────────────────────────────────────
    broadcast_interval_hours: int = Field(default=24, alias="BROADCAST_INTERVAL_HOURS")

    # ── Gameplay — Stamina & Tapping ──────────────────────────────────────
    initial_stamina: int = Field(default=200, alias="INITIAL_STAMINA")
    stamina_regen_per_min: int = Field(default=10, alias="STAMINA_REGEN_PER_MIN")
    max_tap_per_second: int = Field(default=6, alias="MAX_TAP_PER_SECOND")
    base_profit_per_hour: int = Field(default=150, alias="BASE_PROFIT_PER_HOUR")
    vip_profit_multiplier: float = Field(default=3.5, alias="VIP_PROFIT_MULTIPLIER")

    # ── Rewards ───────────────────────────────────────────────────────────
    referral_reward: int = Field(default=120, alias="REFERRAL_REWARD")
    daily_active_reward: int = Field(default=75, alias="DAILY_ACTIVE_REWARD")
    daily_combo_reward: float = Field(default=100000.0, alias="DAILY_COMBO_REWARD")
    daily_cipher_reward: float = Field(default=50000.0, alias="DAILY_CIPHER_REWARD")

    # ── Market Fees ───────────────────────────────────────────────────────
    market_buy_fee_bps: int = Field(default=15, alias="MARKET_BUY_FEE_BPS")
    market_sell_fee_bps: int = Field(default=25, alias="MARKET_SELL_FEE_BPS")

    # ── Exchange API ──────────────────────────────────────────────────────
    exchange_api_base: str = Field(
        default="https://api.binance.com", alias="EXCHANGE_API_BASE"
    )
    exchange_api_key: str = Field(default="", alias="EXCHANGE_API_KEY")
    exchange_api_secret: str = Field(default="", alias="EXCHANGE_API_SECRET")
    enabled_exchanges: str = Field(
        default="binance,bybit", alias="ENABLED_EXCHANGES"
    )

    # ── Airdrop ───────────────────────────────────────────────────────────
    airdrop_reward_min: float = Field(default=10000, alias="AIRDROP_REWARD_MIN")
    airdrop_reward_max: float = Field(default=300000, alias="AIRDROP_REWARD_MAX")
    airdrop_token_symbol: str = Field(default="ADX", alias="AIRDROP_TOKEN_SYMBOL")

    # ── Admin ─────────────────────────────────────────────────────────────
    admin_api_token: str = Field(
        default="change_me_admin_token", alias="ADMIN_API_TOKEN"
    )

    # ── Worker ────────────────────────────────────────────────────────────
    worker_tick_seconds: int = Field(default=15, alias="WORKER_TICK_SECONDS")

    # ── Per-Exchange Keys (all optional) ──────────────────────────────────
    binance_api_key: str = Field(default="", alias="BINANCE_API_KEY")
    binance_api_secret: str = Field(default="", alias="BINANCE_API_SECRET")
    bybit_api_key: str = Field(default="", alias="BYBIT_API_KEY")
    bybit_api_secret: str = Field(default="", alias="BYBIT_API_SECRET")
    okx_api_key: str = Field(default="", alias="OKX_API_KEY")
    okx_api_secret: str = Field(default="", alias="OKX_API_SECRET")
    okx_api_passphrase: str = Field(default="", alias="OKX_API_PASSPHRASE")
    kucoin_api_key: str = Field(default="", alias="KUCOIN_API_KEY")
    kucoin_api_secret: str = Field(default="", alias="KUCOIN_API_SECRET")
    kucoin_api_passphrase: str = Field(default="", alias="KUCOIN_API_PASSPHRASE")

    # ── Computed Properties ───────────────────────────────────────────────

    @property
    def webhook_url(self) -> str:
        return f"{self.webhook_base_url.rstrip('/')}{self.webhook_path}"

    @property
    def admin_id_set(self) -> set[int]:
        return {
            int(v.strip())
            for v in self.admin_ids.split(",")
            if v.strip() and v.strip().isdigit()
        }

    @property
    def vip_id_set(self) -> set[int]:
        return {
            int(v.strip())
            for v in self.vip_ids.split(",")
            if v.strip() and v.strip().isdigit()
        }

    @property
    def enabled_exchange_list(self) -> list[str]:
        return [
            item.strip().lower()
            for item in self.enabled_exchanges.split(",")
            if item.strip()
        ]

    # ── Safe image URLs (never return empty string) ───────────────────────

    @property
    def safe_token_logo_url(self) -> str:
        return self.token_logo_url.strip() or _FALLBACK_TOKEN_LOGO

    @property
    def safe_cover_image_url(self) -> str:
        return self.cover_image_url.strip() or _FALLBACK_COVER

    @property
    def safe_vip_image_url(self) -> str:
        return self.vip_image_url.strip() or _FALLBACK_VIP

    @property
    def safe_market_image_url(self) -> str:
        return self.market_image_url.strip() or _FALLBACK_MARKET

    @property
    def safe_quest_image_url(self) -> str:
        return self.quest_image_url.strip() or _FALLBACK_QUEST


@lru_cache
def get_settings() -> Settings:
    return Settings()
