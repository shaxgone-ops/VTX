"""
VTX Earn Arena — Application Entry Point
==========================================
FastAPI application with:
  - Telegram webhook handling
  - REST API endpoints for Mini App
  - Background tasks (broadcast, worker)
  - Database initialization & card seeding
  - Static file serving for assets
  - CORS for frontend
"""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import async_session_factory, create_tables, dispose_engine
from app.bot.handlers import router as bot_router
from app.webapi import admin_router, api_router

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
#  Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


# ---------------------------------------------------------------------------
#  Bot & Dispatcher
# ---------------------------------------------------------------------------

bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
dp.include_router(bot_router)


# ---------------------------------------------------------------------------
#  Middleware: inject DB session into handler data
# ---------------------------------------------------------------------------

@dp.update.outer_middleware()
async def db_session_middleware(handler, event, data):
    async with async_session_factory() as session:
        data["session"] = session
        return await handler(event, data)


# ---------------------------------------------------------------------------
#  Background tasks
# ---------------------------------------------------------------------------

_background_tasks: list[asyncio.Task] = []


async def _start_broadcast_loop():
    """Start the 24-hour broadcast background task."""
    from app.services.broadcast import broadcast_loop
    await broadcast_loop(bot, async_session_factory)


async def _seed_cards():
    """Seed 305 default cards into the database."""
    from app.services.cards import ensure_default_cards
    async with async_session_factory() as session:
        count = await ensure_default_cards(session)
        if count > 0:
            logger.info("Seeded %d cards into database", count)


# ---------------------------------------------------------------------------
#  Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: runs on startup and shutdown."""
    # ── Startup ───────────────────────────────────────────────────────
    logger.info("Starting VTX Earn Arena...")

    # 1. Create DB tables
    await create_tables()

    # 2. Seed default cards
    try:
        await _seed_cards()
    except Exception as exc:
        logger.error("Card seeding error: %s", exc)

    # 3. Set webhook
    webhook_url = settings.webhook_url
    logger.info("Setting webhook: %s", webhook_url)
    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret,
            drop_pending_updates=True,
        )
        logger.info("Webhook set successfully")
    except Exception as exc:
        logger.error("Webhook setup failed: %s", exc)

    # 4. Start background broadcast loop
    task = asyncio.create_task(_start_broadcast_loop())
    _background_tasks.append(task)

    yield

    # ── Shutdown ──────────────────────────────────────────────────────
    logger.info("Shutting down VTX Earn Arena...")

    # Cancel background tasks
    for task in _background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Delete webhook
    try:
        await bot.delete_webhook()
    except Exception:
        pass

    # Close bot session
    try:
        await bot.session.close()
    except Exception:
        pass

    # Dispose DB engine
    await dispose_engine()

    logger.info("Shutdown complete")


# ---------------------------------------------------------------------------
#  FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
#  CORS — allow frontend origin
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_public_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://web.telegram.org",
        "*",  # In production, restrict this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
#  Mount routers
# ---------------------------------------------------------------------------

app.include_router(api_router)
app.include_router(admin_router)


# ---------------------------------------------------------------------------
#  Static files for assets (token_logo, cover, etc.)
# ---------------------------------------------------------------------------

assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# ---------------------------------------------------------------------------
#  Telegram Webhook endpoint
# ---------------------------------------------------------------------------

@app.post(settings.webhook_path)
async def telegram_webhook(request: Request) -> JSONResponse:
    """Receive and process Telegram updates via webhook."""
    # Verify secret token
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if secret != settings.webhook_secret:
        return JSONResponse({"error": "Forbidden"}, status_code=403)

    try:
        body = await request.json()
        update = Update(**body)
        await dp.feed_update(bot=bot, update=update)
    except Exception as exc:
        logger.error("Webhook processing error: %s", exc, exc_info=True)

    return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
#  Root endpoint
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "version": "2.0.0",
        "frontend": settings.frontend_public_url,
        "docs": "/docs",
    }
