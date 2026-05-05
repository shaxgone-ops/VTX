import time

import httpx

from app.exchanges.base import ExchangeOrderRequest, ExchangeOrderResult


class BybitAdapter:
    exchange_name = "bybit"

    async def fetch_price(self, symbol: str) -> float:
        pair = f"{symbol.upper()}USDT"
        url = "https://api.bybit.com/v5/market/tickers"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params={"category": "spot", "symbol": pair})
            response.raise_for_status()
            payload = response.json()
            entries = payload.get("result", {}).get("list", [])
            if not entries:
                raise ValueError("price_not_found")
            return float(entries[0]["lastPrice"])

    async def place_market_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult:
        price = await self.fetch_price(request.symbol)
        return ExchangeOrderResult(
            exchange=self.exchange_name,
            order_id=f"bb_{int(time.time() * 1000)}",
            status="filled",
            filled_qty=request.quantity,
            avg_price=price,
        )
