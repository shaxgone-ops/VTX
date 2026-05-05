from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User, WithdrawalRequest
from app.services.wallets import get_wallet_for_network

settings = get_settings()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def request_withdrawal(
    session: AsyncSession,
    user: User,
    wallet_address: str | None,
    amount: float,
    network: str = "TON",
    asset_symbol: str | None = None,
) -> tuple[bool, str]:
    if user.is_banned:
        return False, "Account blocked"
    if user.suspicious_score >= 70:
        return False, "Risk level too high"
    if user.withdrawal_locked_until and user.withdrawal_locked_until > now_utc():
        return False, "Withdrawal temporary locked"
    if amount <= 0:
        return False, "Invalid amount"
    if user.total_tokens < amount:
        return False, "Insufficient tokens"
    resolved_wallet = wallet_address or await get_wallet_for_network(session, user, network)
    if not resolved_wallet:
        return False, "Wallet is missing for selected network"
    user.total_tokens -= amount
    user.wallet_address = resolved_wallet
    user.withdrawal_locked_until = now_utc() + timedelta(hours=6)
    row = WithdrawalRequest(
        user_id=user.id,
        wallet_address=resolved_wallet,
        wallet_network=network.strip().upper(),
        asset_symbol=asset_symbol or settings.token_symbol,
        token_amount=amount,
        status="pending",
    )
    session.add(row)
    await session.commit()
    return True, f"Withdrawal request created with amount {amount}"


async def list_pending_withdrawals(session: AsyncSession, limit: int = 20) -> list[WithdrawalRequest]:
    stmt = select(WithdrawalRequest).where(WithdrawalRequest.status == "pending").limit(limit)
    return list((await session.execute(stmt)).scalars().all())


async def review_withdrawal(session: AsyncSession, withdrawal_id: int, approve: bool, reviewer_note: str) -> tuple[bool, str]:
    stmt = select(WithdrawalRequest).where(WithdrawalRequest.id == withdrawal_id)
    row = (await session.execute(stmt)).scalar_one_or_none()
    if not row:
        return False, "Request not found"
    if row.status != "pending":
        return False, "Already reviewed"
    row.status = "approved" if approve else "rejected"
    row.reviewer_note = reviewer_note
    if not approve:
        user = (await session.execute(select(User).where(User.id == row.user_id))).scalar_one_or_none()
        if user:
            user.total_tokens += row.token_amount
    await session.commit()
    return True, row.status
