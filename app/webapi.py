from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services.cards import ensure_default_cards, list_cards_with_user_stage, upgrade_user_card
from app.services.users import get_user_by_telegram_id

router = APIRouter(prefix="/api", tags=["webapp"])


class UpgradePayload(BaseModel):
    telegram_id: int
    card_id: int


@router.get("/cards/{telegram_id}")
async def cards(telegram_id: int) -> dict:
    async with AsyncSessionLocal() as session:
        await ensure_default_cards(session)
        user = await get_user_by_telegram_id(session, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        rows = await list_cards_with_user_stage(session, user)
        return {"cards": rows, "profit_per_hour": user.profit_per_hour, "balance": user.total_tokens}


@router.post("/cards/upgrade")
async def upgrade(payload: UpgradePayload) -> dict:
    async with AsyncSessionLocal() as session:
        user = await get_user_by_telegram_id(session, payload.telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        ok, message, data = await upgrade_user_card(session, user, payload.card_id)
        if not ok:
            raise HTTPException(status_code=400, detail=message)
        return {"ok": True, "message": message, "data": data}
