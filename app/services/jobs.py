import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WorkerJob


async def enqueue_job(session: AsyncSession, job_type: str, payload: dict[str, Any]) -> WorkerJob:
    row = WorkerJob(job_type=job_type, payload_json=json.dumps(payload, ensure_ascii=True), status="pending")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def next_pending_jobs(session: AsyncSession, limit: int = 20) -> list[WorkerJob]:
    stmt = select(WorkerJob).where(WorkerJob.status == "pending").limit(limit)
    return list((await session.execute(stmt)).scalars().all())
