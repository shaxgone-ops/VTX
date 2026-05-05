import time

import httpx

from app.exchanges.base import ExchangeOrderRequest, ExchangeOrderResult


class OkxAdapter:
    exchange_name = "okx"

    async def fetch_price(self, symbol: str) -> float:
        inst_id = f"{symbol.upper()}-USDT"
        url = "https://www.okx.com/api/v5/market/ticker"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params={"instId": inst_id})
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", [])
            if not data:
                raise ValueError("price_not_found")
            return float(data[0]["last"])

    async def place_market_order(self, request: ExchangeOrderRequest) -> ExchangeOrderResult:
        price = await self.fetch_price(request.symbol)
        return ExchangeOrderResult(
            exchange=self.exchange_name,
            order_id=f"okx_{int(time.time() * 1000)}",
            status="filled",
            filled_qty=request.quantity,
            avg_price=price,
        )
