from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserWallet

SUPPORTED_NETWORKS = {"TON", "TRON", "BSC", "ETH", "SOL", "POLYGON"}


async def save_wallet(session: AsyncSession, user: User, network: str, address: str, make_primary: bool = True) -> tuple[bool, str]:
    normalized = network.strip().upper()
    if normalized not in SUPPORTED_NETWORKS:
        return False, "Unsupported network"
    row = (await session.execute(select(UserWallet).where(UserWallet.user_id == user.id, UserWallet.wallet_network == normalized))).scalar_one_or_none()
    if row:
        row.wallet_address = address
        if make_primary:
            row.is_primary = True
    else:
        row = UserWallet(user_id=user.id, wallet_network=normalized, wallet_address=address, is_primary=make_primary)
        session.add(row)
    if make_primary:
        all_rows = list((await session.execute(select(UserWallet).where(UserWallet.user_id == user.id))).scalars().all())
        for item in all_rows:
            item.is_primary = item.wallet_network == normalized
    await session.commit()
    return True, f"Wallet saved for {normalized}"


async def get_wallet_for_network(session: AsyncSession, user: User, network: str) -> str | None:
    normalized = network.strip().upper()
    row = (await session.execute(select(UserWallet).where(UserWallet.user_id == user.id, UserWallet.wallet_network == normalized))).scalar_one_or_none()
    if row:
        return row.wallet_address
    primary = (await session.execute(select(UserWallet).where(UserWallet.user_id == user.id, UserWallet.is_primary.is_(True)))).scalar_one_or_none()
    return primary.wallet_address if primary else None
