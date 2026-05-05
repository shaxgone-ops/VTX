from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exchanges.base import ExchangeOrderRequest
from app.models import MarketOrder, User
from app.services.exchange_router import build_adapters

settings = get_settings()


async def fetch_price(symbol: str) -> float:
    adapters = build_adapters()
    errors: list[str] = []
    for adapter in adapters:
        try:
            return await adapter.fetch_price(symbol)
        except Exception as exc:
            errors.append(f"{adapter.exchange_name}:{exc}")
    raise ValueError("all_exchange_price_fetch_failed:" + "|".join(errors))


def fee_for(side: str, quote_amount: float) -> float:
    bps = settings.market_buy_fee_bps if side == "buy" else settings.market_sell_fee_bps
    return round(quote_amount * bps / 10000, 8)


async def create_market_order(session: AsyncSession, user: User, side: str, token_amount: float) -> MarketOrder:
    adapters = build_adapters()
    adapter = adapters[0]
    request = ExchangeOrderRequest(symbol=settings.token_symbol, side=side, quantity=token_amount)
    result = await adapter.place_market_order(request)
    quote_amount = round(token_amount * result.avg_price, 8)
    fee = fee_for(side=side, quote_amount=quote_amount)
    if side == "sell":
        if user.total_tokens < token_amount:
            raise ValueError("insufficient_tokens")
        user.total_tokens -= token_amount
    order = MarketOrder(
        user_id=user.id,
        side=side,
        token_amount=token_amount,
        quote_amount=quote_amount,
        fee_amount=fee,
        exchange_order_id=result.order_id,
        status=f"{result.status}_{result.exchange}",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order
