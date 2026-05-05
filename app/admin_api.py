from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models import WithdrawalRequest, WorkerJob
from app.services.jobs import enqueue_job

settings = get_settings()
router = APIRouter(prefix="/admin", tags=["admin"])


def check_admin_token(token: str | None) -> None:
    if not token or token != settings.admin_api_token:
        raise HTTPException(status_code=401, detail="Unauthorized")


class QueueWithdrawalPayload(BaseModel):
    withdrawal_id: int


@router.get("/health")
async def admin_health(x_admin_token: str = Header(default="")) -> dict:
    check_admin_token(x_admin_token)
    return {"ok": True}


@router.get("/withdrawals/pending")
async def pending_withdrawals(x_admin_token: str = Header(default="")) -> dict:
    check_admin_token(x_admin_token)
    async with AsyncSessionLocal() as session:
        rows = list((await session.execute(select(WithdrawalRequest).where(WithdrawalRequest.status == "approved").limit(200))).scalars().all())
        return {
            "items": [
                {
                    "id": row.id,
                    "user_id": row.user_id,
                    "network": row.wallet_network,
                    "asset": row.asset_symbol,
                    "amount": row.token_amount,
                    "wallet": row.wallet_address,
                }
                for row in rows
            ]
        }


@router.post("/withdrawals/queue")
async def queue_withdrawal(payload: QueueWithdrawalPayload, x_admin_token: str = Header(default="")) -> dict:
    check_admin_token(x_admin_token)
    async with AsyncSessionLocal() as session:
        row = await enqueue_job(session, "withdrawal_broadcast", {"withdrawal_id": payload.withdrawal_id})
        return {"ok": True, "job_id": row.id}


@router.get("/jobs")
async def list_jobs(x_admin_token: str = Header(default="")) -> dict:
    check_admin_token(x_admin_token)
    async with AsyncSessionLocal() as session:
        rows = list((await session.execute(select(WorkerJob).limit(200))).scalars().all())
        return {
            "items": [
                {
                    "id": row.id,
                    "job_type": row.job_type,
                    "status": row.status,
                    "attempt_count": row.attempt_count,
                    "last_error": row.last_error,
                }
                for row in rows
            ]
        }
