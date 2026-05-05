from contextlib import asynccontextmanager
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers import router
from app.admin_api import router as admin_router
from app.config import get_settings
from app.database import AsyncSessionLocal, engine
from app.models import Base
from app.services.broadcast import broadcast_loop
from app.worker import worker_loop
from app.webapi import router as webapi_router

settings = get_settings()
bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


class SessionMiddleware:
    async def __call__(self, handler, event, data):
        async with AsyncSessionLocal() as session:
            data["session"] = session
            result = await handler(event, data)
            return result


dp.update.outer_middleware(SessionMiddleware())
dp.include_router(router)


@asynccontextmanager
async def lifespan(_: FastAPI):
    broadcast_task = None
    worker_task = None
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await bot.set_webhook(
        url=settings.webhook_url,
        secret_token=settings.webhook_secret,
        allowed_updates=dp.resolve_used_update_types(),
    )
    broadcast_task = asyncio.create_task(broadcast_loop(bot))
    worker_task = asyncio.create_task(worker_loop())
    yield
    if broadcast_task:
        broadcast_task.cancel()
    if worker_task:
        worker_task.cancel()
    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(webapi_router)
app.include_router(admin_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_public_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "name": settings.app_name}


@app.post(settings.webhook_path)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default=""),
) -> dict:
    if x_telegram_bot_api_secret_token != settings.webhook_secret:
        raise HTTPException(status_code=401, detail="invalid secret")
    raw = await request.json()
    update = Update.model_validate(raw)
    await dp.feed_update(bot, update)
    return {"ok": True}
