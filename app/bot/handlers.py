from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import main_menu
from app.config import get_settings
from app.models import UserQuestProgress
from app.services.airdrop import apply_airdrop_rewards, create_monthly_snapshot, open_or_get_monthly_epoch
from app.services.anti_abuse import register_fingerprint
from app.services.audit import write_audit
from app.services.cards import ensure_default_cards
from app.services.game import process_tap
from app.services.i18n import normalize_locale
from app.services.leaderboard import format_leaderboard, top_by_balance
from app.services.market import create_market_order
from app.services.quests import claim_quest, ensure_default_quests, format_quests, list_active_quests, update_progress
from app.services.referrals import register_referral
from app.services.rewards import award_daily_active_bonus, boost_profit_per_hour
from app.services.users import create_or_update_user, get_user_by_telegram_id
from app.services.vip import activate_vip, sync_vip_expiry
from app.services.wallets import save_wallet
from app.services.withdrawals import list_pending_withdrawals, request_withdrawal, review_withdrawal

router = Router()
settings = get_settings()


def parse_invite_code(payload: str | None) -> int | None:
    if not payload:
        return None
    if not payload.startswith("ref_"):
        return None
    raw = payload.replace("ref_", "").strip()
    if not raw.isdigit():
        return None
    return int(raw)


@router.message(CommandStart(deep_link=True))
@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession) -> None:
    await ensure_default_quests(session)
    await ensure_default_cards(session)
    inviter_telegram_id = parse_invite_code(message.text.split(maxsplit=1)[1] if message.text and " " in message.text else None)
    if settings.whitelist_only and message.from_user.id not in settings.vip_id_set and message.from_user.id not in settings.admin_id_set:
        await message.answer_photo(
            photo=settings.token_logo_url,
            caption="Access blocked. This bot is private.",
        )
        return
    inviter_id = None
    inviter_user = None
    if inviter_telegram_id:
        inviter_user = await get_user_by_telegram_id(session, inviter_telegram_id)
        if inviter_user:
            inviter_id = inviter_user.id
    user = await create_or_update_user(
        session=session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        invited_by_user_id=inviter_id,
    )
    user.locale = normalize_locale(message.from_user.language_code)
    await session.commit()
    await sync_vip_expiry(session, user)
    if inviter_user and inviter_user.id != user.id:
        await register_referral(session, inviter=inviter_user, invitee=user)
    invite_link = f"https://t.me/{(await message.bot.get_me()).username}?start=ref_{message.from_user.id}"
    text = (
        f"{settings.token_name}\n"
        f"Balance: {round(user.total_tokens, 4)} {settings.token_symbol}\n"
        f"PPH: {round(user.profit_per_hour, 2)}\n"
        f"Stamina: {user.stamina}\n"
        f"Invite: {invite_link}"
    )
    await message.answer_photo(photo=settings.token_logo_url, caption=text, reply_markup=main_menu(settings.frontend_public_url))


@router.callback_query(F.data.startswith("play_tap_"))
async def tap_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    amount = int(callback.data.replace("play_tap_", ""))
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    result = await process_tap(session=session, user=user, tap_amount=amount)
    await update_progress(session=session, user=user)
    if not result["ok"]:
        if result["reason"] == "stamina_empty":
            await callback.answer("Stamina empty", show_alert=True)
            return
        if result["reason"] == "banned":
            await callback.answer("Account blocked", show_alert=True)
            return
        await callback.answer("Suspicious tap detected", show_alert=True)
        return
    text = (
        f"Tap accepted\n"
        f"Earned: {result['gain_tokens']} {settings.token_symbol}\n"
        f"Balance: {round(result['total_tokens'], 4)} {settings.token_symbol}\n"
        f"Stamina left: {result['stamina_left']}\n"
        f"Combo: {result['combo']}"
    )
    await callback.message.edit_caption(caption=text, reply_markup=main_menu(settings.frontend_public_url))
    await callback.answer()


@router.callback_query(F.data == "profile_show")
async def profile_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    is_vip_text = "VIP" if user.is_vip else "STANDARD"
    text = (
        f"Profile\n"
        f"Tier: {is_vip_text}\n"
        f"Balance: {round(user.total_tokens, 4)} {settings.token_symbol}\n"
        f"PPH: {round(user.profit_per_hour, 2)}\n"
        f"Stamina: {user.stamina}\n"
        f"Risk Score: {user.suspicious_score}"
    )
    await callback.message.edit_caption(caption=text, reply_markup=main_menu(settings.frontend_public_url))
    await callback.answer()


@router.callback_query(F.data == "daily_reward")
async def daily_reward_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    ok = await award_daily_active_bonus(session, user)
    if not ok:
        await callback.answer("Play first, then claim", show_alert=True)
        return
    await callback.answer(f"Reward added: {settings.daily_active_reward}", show_alert=True)


@router.callback_query(F.data.startswith("boost_pph_"))
async def boost_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    delta = int(callback.data.replace("boost_pph_", ""))
    if user.total_tokens < delta:
        await callback.answer("Need more tokens for boost", show_alert=True)
        return
    user.total_tokens -= delta
    updated = await boost_profit_per_hour(session, user, delta=delta)
    await callback.answer(f"PPH boosted to {round(updated.profit_per_hour, 2)}", show_alert=True)


@router.callback_query(F.data.startswith("market_sell_"))
async def market_sell_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    amount = float(callback.data.replace("market_sell_", ""))
    try:
        order = await create_market_order(session=session, user=user, side="sell", token_amount=amount)
    except ValueError:
        await callback.answer("Insufficient token balance", show_alert=True)
        return
    await callback.answer(
        f"Order done. Quote: {order.quote_amount} Fee: {order.fee_amount}",
        show_alert=True,
    )


@router.callback_query(F.data == "top_balance")
async def top_balance_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    rows = await top_by_balance(session, limit=15)
    text = format_leaderboard(rows, metric="balance")
    await callback.message.edit_caption(caption=text, reply_markup=main_menu(settings.frontend_public_url))
    await callback.answer()


@router.callback_query(F.data == "quest_board")
async def quest_board_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    quests = await list_active_quests(session)
    stmt = select(UserQuestProgress).where(UserQuestProgress.user_id == user.id)
    rows = list((await session.execute(stmt)).scalars().all())
    progress_map = {row.quest_id: row for row in rows}
    text = format_quests(quests, progress_map)
    await callback.message.edit_caption(caption=text, reply_markup=main_menu(settings.frontend_public_url))
    await callback.answer()


@router.callback_query(F.data.startswith("quest_claim_"))
async def quest_claim_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    quest_code = callback.data.replace("quest_claim_", "")
    ok, message = await claim_quest(session, user, quest_code=quest_code)
    await callback.answer(message, show_alert=True)
    if ok:
        await write_audit(
            session=session,
            action_code="quest_claim",
            details={"quest_code": quest_code, "telegram_id": callback.from_user.id},
            actor_user=user,
        )


@router.callback_query(F.data.startswith("withdraw_"))
async def withdraw_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    if not user:
        await callback.answer("Send /start first", show_alert=True)
        return
    amount = float(callback.data.replace("withdraw_", ""))
    ok, message = await request_withdrawal(
        session,
        user,
        wallet_address=user.wallet_address,
        amount=amount,
        network="TON",
        asset_symbol=settings.token_symbol,
    )
    await callback.answer(message, show_alert=True)


@router.message(F.text.startswith("/setwallet "))
async def set_wallet_handler(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user:
        await message.answer("Send /start first")
        return
    wallet = message.text.replace("/setwallet ", "", 1).strip()
    user.wallet_address = wallet
    await session.commit()
    await message.answer("Wallet updated")


@router.message(F.text.startswith("/wallet "))
async def wallet_network_handler(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user:
        await message.answer("Send /start first")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Usage: /wallet NETWORK ADDRESS")
        return
    network = args[1]
    address = args[2]
    ok, text = await save_wallet(session, user, network=network, address=address, make_primary=True)
    await message.answer(text if ok else f"Failed: {text}")


@router.message(F.text.startswith("/fingerprint "))
async def fingerprint_handler(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user:
        await message.answer("Send /start first")
        return
    raw_fingerprint = message.text.replace("/fingerprint ", "", 1).strip()
    ok, text = await register_fingerprint(session, user, raw_fingerprint=raw_fingerprint)
    if not ok:
        await message.answer("Fingerprint failed")
        return
    await message.answer(text)


@router.message(F.text.startswith("/admin_vip "))
async def admin_vip_handler(message: Message, session: AsyncSession) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Usage: /admin_vip telegram_id days")
        return
    target_telegram_id = int(args[1])
    days = int(args[2])
    target = await get_user_by_telegram_id(session, target_telegram_id)
    if not target:
        await message.answer("User not found")
        return
    await activate_vip(session, target, days=days)
    await write_audit(
        session=session,
        action_code="admin_vip_activate",
        details={"target_telegram_id": target_telegram_id, "days": days},
    )
    await message.answer(f"VIP activated for {days} days")


@router.message(F.text == "/admin_withdrawals")
async def admin_pending_withdrawals(message: Message, session: AsyncSession) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return
    rows = await list_pending_withdrawals(session, limit=20)
    if not rows:
        await message.answer("No pending withdrawals")
        return
    lines = ["Pending withdrawals"]
    for row in rows:
        lines.append(f"id={row.id} user={row.user_id} amount={row.token_amount} wallet={row.wallet_address}")
    await message.answer("\n".join(lines))


@router.message(F.text.startswith("/admin_review "))
async def admin_review_withdrawal(message: Message, session: AsyncSession) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer("Usage: /admin_review request_id approve_or_reject note")
        return
    request_id = int(args[1])
    mode = args[2].strip().lower()
    note = args[3].strip()
    approve = mode == "approve"
    ok, status = await review_withdrawal(session, withdrawal_id=request_id, approve=approve, reviewer_note=note)
    if not ok:
        await message.answer(status)
        return
    await write_audit(
        session=session,
        action_code="admin_review_withdrawal",
        details={"request_id": request_id, "status": status, "note": note},
    )
    await message.answer(f"Withdrawal updated: {status}")


@router.message(F.text.startswith("/admin_airdrop "))
async def admin_run_airdrop(message: Message, session: AsyncSession) -> None:
    if message.from_user.id not in settings.admin_id_set:
        return
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Usage: /admin_airdrop month_key pool_tokens")
        return
    month_key = args[1]
    pool_tokens = float(args[2])
    starts_at = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ends_at = (starts_at + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    epoch = await open_or_get_monthly_epoch(session, month_key, starts_at=starts_at, ends_at=ends_at, pool_tokens=pool_tokens)
    snap_count = await create_monthly_snapshot(session, epoch)
    applied_count = await apply_airdrop_rewards(session, epoch)
    await write_audit(
        session=session,
        action_code="admin_airdrop_run",
        details={"month_key": month_key, "pool_tokens": pool_tokens, "snapshots": snap_count, "applied": applied_count},
    )
    await message.answer(f"Airdrop completed. snapshots={snap_count} applied={applied_count}")
