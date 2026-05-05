import time

import httpx

from app.config import get_settings
from app.exchanges.base import ExchangeOrderRequest, ExchangeOrderResult

settings = get_settings()


class BinanceAdapter:
    exchange_name = "binance"

    async def fetch_price(self, symbol: str) -> float:
        pair = f"{symbol.upper()}USDT"
        url = "https://api.binance.com/api/v3/ticker/price"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params={"symbol": pair})
            response.raise_for_status()
            payload = response.json()
            return float(payload["price"])

    async def place_market_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult:
        price = await self.fetch_price(request.symbol)
        return ExchangeOrderResult(
            exchange=self.exchange_name,
            order_id=f"bn_{int(time.time() * 1000)}",
            status="filled",
            filled_qty=request.quantity,
            avg_price=price,
        )
