"""
VTX Earn Arena — SQLAlchemy ORM Models
=======================================
Every table the application uses lives here.
Models are grouped logically:
  1. Core user & authentication
  2. Gameplay — taps, stamina
  3. Cards & upgrades
  4. Quests & daily challenges
  5. Referrals & social
  6. Market & exchange orders
  7. Airdrop & token distribution
  8. Withdrawal & payout
  9. Admin & audit
"""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ===========================================================================
#  1.  CORE USER
# ===========================================================================

class User(Base):
    """Central user record, one row per Telegram account."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    invited_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # ── Status flags ──────────────────────────────────────────────────────
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Economy ───────────────────────────────────────────────────────────
    total_tokens: Mapped[float] = mapped_column(Float, default=0)
    profit_per_hour: Mapped[float] = mapped_column(Float, default=0)

    # ── Stamina ───────────────────────────────────────────────────────────
    stamina: Mapped[int] = mapped_column(Integer, default=0)
    last_stamina_sync_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # ── Tap stats ─────────────────────────────────────────────────────────
    last_tap_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    tap_combo_counter: Mapped[int] = mapped_column(Integer, default=0)
    lifetime_taps: Mapped[int] = mapped_column(Integer, default=0)
    daily_taps: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # ── Anti-cheat ────────────────────────────────────────────────────────
    suspicious_score: Mapped[int] = mapped_column(Integer, default=0)

    # ── Progression ───────────────────────────────────────────────────────
    level: Mapped[int] = mapped_column(Integer, default=1)
    last_reward_claim_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── VIP ───────────────────────────────────────────────────────────────
    vip_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Wallet ────────────────────────────────────────────────────────────
    wallet_address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    withdrawal_locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Locale (legacy field kept for compat) ─────────────────────────────
    locale: Mapped[str | None] = mapped_column(String(12), nullable=True)

    # ── Offline earnings tracker ──────────────────────────────────────────
    last_earnings_sync_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # ── Relationships ─────────────────────────────────────────────────────
    invited_by = relationship("User", remote_side=[id], uselist=False)


# ===========================================================================
#  2.  GAMEPLAY — TAP EVENTS
# ===========================================================================

class TapEvent(Base):
    """Records every accepted tap batch for analytics and anti-cheat."""
    __tablename__ = "tap_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    tap_amount: Mapped[int] = mapped_column(Integer)
    gain_tokens: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  3.  CARDS & UPGRADES
# ===========================================================================

class CardDefinition(Base):
    """
    Master card catalog.
    Each card belongs to a category and has a rarity tier.
    Max 15 upgrade stages; profit per hour scales from
    stage_profit_min (stage 1) to stage_profit_max (stage 15).
    """
    __tablename__ = "card_definitions"
    __table_args__ = (UniqueConstraint("code", name="uq_card_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(32), default="specials", index=True)
    rarity: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str] = mapped_column(String(512))
    base_cost: Mapped[float] = mapped_column(Float)
    stage_profit_min: Mapped[float] = mapped_column(Float)
    stage_profit_max: Mapped[float] = mapped_column(Float)
    max_stage: Mapped[int] = mapped_column(Integer, default=15)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class UserCard(Base):
    """Tracks which stage a user has reached on each card."""
    __tablename__ = "user_cards"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    card_id: Mapped[int] = mapped_column(
        ForeignKey("card_definitions.id"), index=True
    )
    stage: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


# ===========================================================================
#  4.  QUESTS & DAILY CHALLENGES
# ===========================================================================

class Quest(Base):
    """Defines a quest objective and its rewards."""
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    quest_type: Mapped[str] = mapped_column(String(64))
    target_value: Mapped[int] = mapped_column(Integer)
    reward_tokens: Mapped[float] = mapped_column(Float)
    reward_pph: Mapped[float] = mapped_column(Float, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class UserQuestProgress(Base):
    """Per-user progress on each quest."""
    __tablename__ = "user_quest_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "quest_id", name="uq_user_quest"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quest_id: Mapped[int] = mapped_column(ForeignKey("quests.id"), index=True)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class DailyCombo(Base):
    """Admin sets 3 cards per day.  Users who upgrade all 3 → big bonus."""
    __tablename__ = "daily_combos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_key: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    card_id_1: Mapped[int] = mapped_column(Integer)
    card_id_2: Mapped[int] = mapped_column(Integer)
    card_id_3: Mapped[int] = mapped_column(Integer)
    reward_tokens: Mapped[float] = mapped_column(Float, default=100000)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class UserDailyComboStatus(Base):
    """Tracks whether a user has claimed the daily combo bonus."""
    __tablename__ = "user_daily_combo_status"
    __table_args__ = (
        UniqueConstraint("user_id", "date_key", name="uq_user_daily_combo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date_key: Mapped[str] = mapped_column(String(16))
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class DailyCipher(Base):
    """Admin sets a secret word each day.  Users who guess → bonus."""
    __tablename__ = "daily_ciphers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_key: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    cipher_answer: Mapped[str] = mapped_column(String(64))
    reward_tokens: Mapped[float] = mapped_column(Float, default=50000)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class UserDailyCipherStatus(Base):
    """Tracks whether a user has solved today's cipher."""
    __tablename__ = "user_daily_cipher_status"
    __table_args__ = (
        UniqueConstraint("user_id", "date_key", name="uq_user_daily_cipher"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date_key: Mapped[str] = mapped_column(String(16))
    is_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    solved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


# ===========================================================================
#  5.  REFERRALS
# ===========================================================================

class Referral(Base):
    """Tracks invitation links between users."""
    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("inviter_id", "invitee_id", name="uq_referral_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    invitee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reward_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  6.  MARKET & EXCHANGE ORDERS
# ===========================================================================

class MarketOrder(Base):
    """Records buy/sell orders placed on connected exchanges."""
    __tablename__ = "market_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    side: Mapped[str] = mapped_column(String(12))
    token_amount: Mapped[float] = mapped_column(Float)
    quote_amount: Mapped[float] = mapped_column(Float)
    fee_amount: Mapped[float] = mapped_column(Float)
    exchange_order_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    status: Mapped[str] = mapped_column(String(24), default="created")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  7.  AIRDROP & TOKEN DISTRIBUTION
# ===========================================================================

class AirdropEpoch(Base):
    """One epoch per month.  Admin triggers snapshot + distribution."""
    __tablename__ = "airdrop_epochs"
    __table_args__ = (UniqueConstraint("month_key", name="uq_airdrop_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month_key: Mapped[str] = mapped_column(String(16), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_pool_tokens: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="planned")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AirdropSnapshot(Base):
    """Per-user scoring snapshot within an epoch."""
    __tablename__ = "airdrop_snapshots"
    __table_args__ = (
        UniqueConstraint("epoch_id", "user_id", name="uq_snapshot_user_epoch"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    epoch_id: Mapped[int] = mapped_column(
        ForeignKey("airdrop_epochs.id"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    weighted_score: Mapped[float] = mapped_column(Float, default=0)
    airdrop_amount: Mapped[float] = mapped_column(Float, default=0)
    is_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  8.  WITHDRAWAL & PAYOUT
# ===========================================================================

class WithdrawalRequest(Base):
    """User requests to withdraw tokens to an external wallet."""
    __tablename__ = "withdrawal_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    wallet_address: Mapped[str] = mapped_column(String(256))
    wallet_network: Mapped[str] = mapped_column(String(32), default="TON")
    asset_symbol: Mapped[str] = mapped_column(String(24), default="VTX")
    token_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    reviewer_note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class PayoutTx(Base):
    """On-chain transaction record for an approved withdrawal."""
    __tablename__ = "payout_txs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    withdrawal_request_id: Mapped[int] = mapped_column(
        ForeignKey("withdrawal_requests.id"), index=True
    )
    network: Mapped[str] = mapped_column(String(32))
    tx_hash: Mapped[str] = mapped_column(String(256), index=True)
    status: Mapped[str] = mapped_column(String(24), default="broadcasted")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  9.  DEVICE FINGERPRINT & ANTI-ABUSE
# ===========================================================================

class DeviceFingerprint(Base):
    """Stores hashed device fingerprints to detect multi-accounting."""
    __tablename__ = "device_fingerprints"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "fingerprint_hash", name="uq_user_fingerprint"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    fingerprint_hash: Mapped[str] = mapped_column(String(128), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    risk_flagged: Mapped[bool] = mapped_column(Boolean, default=False)


# ===========================================================================
#  10.  ADMIN & AUDIT
# ===========================================================================

class AuditLog(Base):
    """Immutable log of admin and system actions."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    action_code: Mapped[str] = mapped_column(String(64), index=True)
    details_json: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class BroadcastLog(Base):
    """Records each broadcast to all users."""
    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_key: Mapped[str] = mapped_column(String(64), index=True)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  11.  WALLETS
# ===========================================================================

class UserWallet(Base):
    """Multi-network wallet addresses for a user."""
    __tablename__ = "user_wallets"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "wallet_network", name="uq_user_wallet_network"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    wallet_network: Mapped[str] = mapped_column(String(32))
    wallet_address: Mapped[str] = mapped_column(String(256))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


# ===========================================================================
#  12.  WORKER JOBS
# ===========================================================================

class WorkerJob(Base):
    """Background job queue (withdrawal broadcasts, etc.)."""
    __tablename__ = "worker_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[str] = mapped_column(String(4096))
    status: Mapped[str] = mapped_column(
        String(24), default="pending", index=True
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )