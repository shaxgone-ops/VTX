from dataclasses import dataclass
from typing import Protocol


@dataclass
class ExchangeOrderRequest:
    symbol: str
    side: str
    quantity: float


@dataclass
class ExchangeOrderResult:
    exchange: str
    order_id: str
    status: str
    filled_qty: float
    avg_price: float


class ExchangeAdapter(Protocol):
    exchange_name: str

    async def fetch_price(self, symbol: str) -> float:
        ...

    async def place_market_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult:
        ...
