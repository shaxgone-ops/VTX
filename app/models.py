from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    invited_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_vip: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    total_tokens: Mapped[float] = mapped_column(Float, default=0)
    profit_per_hour: Mapped[float] = mapped_column(Float, default=0)
    stamina: Mapped[int] = mapped_column(Integer, default=0)
    last_stamina_sync_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_tap_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tap_combo_counter: Mapped[int] = mapped_column(Integer, default=0)
    suspicious_score: Mapped[int] = mapped_column(Integer, default=0)
    lifetime_taps: Mapped[int] = mapped_column(Integer, default=0)
    daily_taps: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_reset_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    level: Mapped[int] = mapped_column(Integer, default=1)
    last_reward_claim_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    withdrawal_locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    vip_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    wallet_address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    locale: Mapped[str | None] = mapped_column(String(12), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invited_by = relationship("User", remote_side=[id], uselist=False)


class TapEvent(Base):
    __tablename__ = "tap_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    tap_amount: Mapped[int] = mapped_column(Integer)
    gain_tokens: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (UniqueConstraint("inviter_id", "invitee_id", name="uq_referral_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    invitee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reward_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketOrder(Base):
    __tablename__ = "market_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    side: Mapped[str] = mapped_column(String(12))
    token_amount: Mapped[float] = mapped_column(Float)
    quote_amount: Mapped[float] = mapped_column(Float)
    fee_amount: Mapped[float] = mapped_column(Float)
    exchange_order_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Quest(Base):
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    quest_type: Mapped[str] = mapped_column(String(64))
    target_value: Mapped[int] = mapped_column(Integer)
    reward_tokens: Mapped[float] = mapped_column(Float)
    reward_pph: Mapped[float] = mapped_column(Float, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserQuestProgress(Base):
    __tablename__ = "user_quest_progress"
    __table_args__ = (UniqueConstraint("user_id", "quest_id", name="uq_user_quest"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quest_id: Mapped[int] = mapped_column(ForeignKey("quests.id"), index=True)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeviceFingerprint(Base):
    __tablename__ = "device_fingerprints"
    __table_args__ = (UniqueConstraint("user_id", "fingerprint_hash", name="uq_user_fingerprint"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    fingerprint_hash: Mapped[str] = mapped_column(String(128), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    risk_flagged: Mapped[bool] = mapped_column(Boolean, default=False)


class AirdropEpoch(Base):
    __tablename__ = "airdrop_epochs"
    __table_args__ = (UniqueConstraint("month_key", name="uq_airdrop_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month_key: Mapped[str] = mapped_column(String(16), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)
    total_pool_tokens: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="planned")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AirdropSnapshot(Base):
    __tablename__ = "airdrop_snapshots"
    __table_args__ = (UniqueConstraint("epoch_id", "user_id", name="uq_snapshot_user_epoch"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    epoch_id: Mapped[int] = mapped_column(ForeignKey("airdrop_epochs.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    weighted_score: Mapped[float] = mapped_column(Float, default=0)
    airdrop_amount: Mapped[float] = mapped_column(Float, default=0)
    is_eligible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    wallet_address: Mapped[str] = mapped_column(String(256))
    wallet_network: Mapped[str] = mapped_column(String(32), default="TON")
    asset_symbol: Mapped[str] = mapped_column(String(24), default="VTX")
    token_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    reviewer_note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action_code: Mapped[str] = mapped_column(String(64), index=True)
    details_json: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CardDefinition(Base):
    __tablename__ = "card_definitions"
    __table_args__ = (UniqueConstraint("code", name="uq_card_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(160))
    rarity: Mapped[str] = mapped_column(String(32))
    image_url: Mapped[str] = mapped_column(String(512))
    base_cost: Mapped[float] = mapped_column(Float)
    stage_profit_min: Mapped[float] = mapped_column(Float)
    stage_profit_max: Mapped[float] = mapped_column(Float)
    max_stage: Mapped[int] = mapped_column(Integer, default=15)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserCard(Base):
    __tablename__ = "user_cards"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("card_definitions.id"), index=True)
    stage: Mapped[int] = mapped_column(Integer, default=0)
    total_spent: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_key: Mapped[str] = mapped_column(String(64), index=True)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserWallet(Base):
    __tablename__ = "user_wallets"
    __table_args__ = (UniqueConstraint("user_id", "wallet_network", name="uq_user_wallet_network"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    wallet_network: Mapped[str] = mapped_column(String(32))
    wallet_address: Mapped[str] = mapped_column(String(256))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WorkerJob(Base):
    __tablename__ = "worker_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[str] = mapped_column(String(4096))
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PayoutTx(Base):
    __tablename__ = "payout_txs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    withdrawal_request_id: Mapped[int] = mapped_column(ForeignKey("withdrawal_requests.id"), index=True)
    network: Mapped[str] = mapped_column(String(32))
    tx_hash: Mapped[str] = mapped_column(String(256), index=True)
    status: Mapped[str] = mapped_column(String(24), default="broadcasted")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
