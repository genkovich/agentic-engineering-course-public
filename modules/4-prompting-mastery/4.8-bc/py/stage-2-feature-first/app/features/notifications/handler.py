from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.notifications.repository import Repository
from app.features.notifications.service import Service
from app.shared.db import get_session

router = APIRouter(tags=["notifications"])


class SendTestReq(BaseModel):
    user_id: str
    channel: str | None = None
    payload: str | None = None


class SendTestResp(BaseModel):
    notification_id: str
    channel: str
    sent_at: datetime | None


@router.post("/notifications/test", response_model=SendTestResp)
async def send_test(
    req: SendTestReq, session: AsyncSession = Depends(get_session)
) -> SendTestResp:
    try:
        uid = UUID(req.user_id)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_user_id"
        ) from exc
    channel = req.channel or "email"
    payload = req.payload or "test notification"
    svc = Service(Repository(session))
    n = await svc.send(uid, channel, payload)
    return SendTestResp(
        notification_id=str(n.id), channel=n.channel, sent_at=n.sent_at
    )
