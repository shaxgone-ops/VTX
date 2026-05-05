import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PayoutTx, WithdrawalRequest


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def fake_tx_hash(seed: str) -> str:
    return "0x" + hashlib.sha256(seed.encode("utf-8")).hexdigest()


async def broadcast_withdrawal(session: AsyncSession, row: WithdrawalRequest) -> tuple[bool, str]:
    if row.status != "approved":
        return False, "Withdrawal is not approved"
    tx_hash = fake_tx_hash(f"{row.id}:{row.wallet_network}:{row.wallet_address}:{row.token_amount}")
    session.add(PayoutTx(withdrawal_request_id=row.id, network=row.wallet_network, tx_hash=tx_hash, status="broadcasted"))
    row.status = "broadcasted"
    await session.commit()
    return True, tx_hash


async def confirm_broadcasts(session: AsyncSession, limit: int = 100) -> int:
    rows = list((await session.execute(select(PayoutTx).where(PayoutTx.status == "broadcasted").limit(limit))).scalars().all())
    confirmed = 0
    for tx in rows:
        tx.status = "confirmed"
        withdrawal = (await session.execute(select(WithdrawalRequest).where(WithdrawalRequest.id == tx.withdrawal_request_id))).scalar_one_or_none()
        if withdrawal:
            withdrawal.status = "completed"
        confirmed += 1
    await session.commit()
    return confirmed
