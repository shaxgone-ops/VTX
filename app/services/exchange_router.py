from app.config import get_settings
from app.exchanges import BinanceAdapter, BybitAdapter, ExchangeAdapter, KucoinAdapter, OkxAdapter

settings = get_settings()


def build_adapters() -> list[ExchangeAdapter]:
    mapping = {
        "binance": BinanceAdapter,
        "bybit": BybitAdapter,
        "okx": OkxAdapter,
        "kucoin": KucoinAdapter,
    }
    adapters: list[ExchangeAdapter] = []
    for name in settings.enabled_exchange_list:
        adapter_cls = mapping.get(name)
        if adapter_cls:
            adapters.append(adapter_cls())
    if not adapters:
        adapters.append(BinanceAdapter())
    return adapters
