import asyncio
import json

from sqlalchemy import select

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models import WithdrawalRequest
from app.services.jobs import next_pending_jobs
from app.services.payout import broadcast_withdrawal, confirm_broadcasts

settings = get_settings()


async def process_job(job_id: int) -> None:
    async with AsyncSessionLocal() as session:
        stmt = select(WithdrawalRequest).where(WithdrawalRequest.id == job_id)
        row = (await session.execute(stmt)).scalar_one_or_none()
        if not row:
            return
        await broadcast_withdrawal(session, row)


async def process_queue_once() -> None:
    async with AsyncSessionLocal() as session:
        jobs = await next_pending_jobs(session, limit=30)
        for job in jobs:
            try:
                payload = json.loads(job.payload_json)
                if job.job_type == "withdrawal_broadcast":
                    await process_job(int(payload["withdrawal_id"]))
                job.status = "completed"
                job.last_error = None
            except Exception as exc:
                job.attempt_count += 1
                job.last_error = str(exc)
                job.status = "failed" if job.attempt_count >= 5 else "pending"
        await session.commit()


async def worker_loop() -> None:
    while True:
        await process_queue_once()
        async with AsyncSessionLocal() as session:
            await confirm_broadcasts(session, limit=200)
        await asyncio.sleep(max(3, settings.worker_tick_seconds))
