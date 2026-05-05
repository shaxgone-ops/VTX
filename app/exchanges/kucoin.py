import time

import httpx

from app.exchanges.base import ExchangeOrderRequest, ExchangeOrderResult


class KucoinAdapter:
    exchange_name = "kucoin"

    async def fetch_price(self, symbol: str) -> float:
        pair = f"{symbol.upper()}-USDT"
        url = "https://api.kucoin.com/api/v1/market/orderbook/level1"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params={"symbol": pair})
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", {})
            if "price" not in data:
                raise ValueError("price_not_found")
            return float(data["price"])

    async def place_market_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult:
        price = await self.fetch_price(request.symbol)
        return ExchangeOrderResult(
            exchange=self.exchange_name,
            order_id=f"kc_{int(time.time() * 1000)}",
            status="filled",
            filled_qty=request.quantity,
            avg_price=price,
        )
