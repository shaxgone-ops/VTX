"""
VTX Earn Arena — Database Setup
=================================
AsyncPG + SQLAlchemy async engine and session factory.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.models import Base

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
#  Engine & session factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.postgres_dsn,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
#  Create all tables
# ---------------------------------------------------------------------------

async def create_tables() -> None:
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")


# ---------------------------------------------------------------------------
#  Shutdown
# ---------------------------------------------------------------------------

async def dispose_engine() -> None:
    """Dispose the engine on shutdown."""
    await engine.dispose()
    logger.info("Database engine disposed")
