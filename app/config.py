from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(alias="APP_NAME")
    environment: Literal["development", "production"] = Field(alias="ENVIRONMENT")
    bot_token: str = Field(alias="BOT_TOKEN")
    webhook_base_url: str = Field(alias="WEBHOOK_BASE_URL")
    webhook_path: str = Field(alias="WEBHOOK_PATH")
    webhook_secret: str = Field(alias="WEBHOOK_SECRET")
    postgres_dsn: str = Field(alias="POSTGRES_DSN")
    admin_ids: str = Field(alias="ADMIN_IDS")
    vip_ids: str = Field(alias="VIP_IDS")
    whitelist_only: bool = Field(alias="WHITELIST_ONLY")
    token_symbol: str = Field(alias="TOKEN_SYMBOL")
    token_name: str = Field(alias="TOKEN_NAME")
    token_logo_url: str = Field(alias="TOKEN_LOGO_URL")
    cover_image_url: str = Field(alias="COVER_IMAGE_URL")
    vip_image_url: str = Field(alias="VIP_IMAGE_URL")
    market_image_url: str = Field(alias="MARKET_IMAGE_URL")
    quest_image_url: str = Field(alias="QUEST_IMAGE_URL")
    frontend_public_url: str = Field(alias="FRONTEND_PUBLIC_URL")
    backend_public_url: str = Field(alias="BACKEND_PUBLIC_URL")
    broadcast_interval_hours: int = Field(default=24, alias="BROADCAST_INTERVAL_HOURS")
    initial_stamina: int = Field(alias="INITIAL_STAMINA")
    stamina_regen_per_min: int = Field(alias="STAMINA_REGEN_PER_MIN")
    max_tap_per_second: int = Field(alias="MAX_TAP_PER_SECOND")
    base_profit_per_hour: int = Field(alias="BASE_PROFIT_PER_HOUR")
    vip_profit_multiplier: float = Field(alias="VIP_PROFIT_MULTIPLIER")
    referral_reward: int = Field(alias="REFERRAL_REWARD")
    daily_active_reward: int = Field(alias="DAILY_ACTIVE_REWARD")
    market_buy_fee_bps: int = Field(alias="MARKET_BUY_FEE_BPS")
    market_sell_fee_bps: int = Field(alias="MARKET_SELL_FEE_BPS")
    exchange_api_base: str = Field(alias="EXCHANGE_API_BASE")
    exchange_api_key: str = Field(alias="EXCHANGE_API_KEY")
    exchange_api_secret: str = Field(alias="EXCHANGE_API_SECRET")
    enabled_exchanges: str = Field(default="binance,bybit,okx,kucoin", alias="ENABLED_EXCHANGES")
    airdrop_reward_min: float = Field(default=100000, alias="AIRDROP_REWARD_MIN")
    airdrop_reward_max: float = Field(default=300000, alias="AIRDROP_REWARD_MAX")
    airdrop_token_symbol: str = Field(default="ADX", alias="AIRDROP_TOKEN_SYMBOL")
    admin_api_token: str = Field(default="change_me_admin_token", alias="ADMIN_API_TOKEN")
    worker_tick_seconds: int = Field(default=15, alias="WORKER_TICK_SECONDS")

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

    @property
    def webhook_url(self) -> str:
        return f"{self.webhook_base_url.rstrip('/')}{self.webhook_path}"

    @property
    def admin_id_set(self) -> set[int]:
        return {int(value.strip()) for value in self.admin_ids.split(",") if value.strip()}

    @property
    def vip_id_set(self) -> set[int]:
        return {int(value.strip()) for value in self.vip_ids.split(",") if value.strip()}

    @property
    def enabled_exchange_list(self) -> list[str]:
        return [item.strip().lower() for item in self.enabled_exchanges.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
