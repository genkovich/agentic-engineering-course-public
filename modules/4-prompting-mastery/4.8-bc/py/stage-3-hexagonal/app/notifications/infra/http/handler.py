"""Notifications HTTP handler — POST /notifications/test."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.notifications.app.service import Service
from app.notifications.domain.notification import Channel


class SendTestReq(BaseModel):
    user_id: str
    channel: str | None = None
    payload: str | None = None


class SendTestResp(BaseModel):
    notification_id: str
    channel: str
    sent_at: datetime | None


def build_router(svc: Service) -> APIRouter:
    router = APIRouter(tags=["notifications"])

    @router.post("/notifications/test", response_model=SendTestResp)
    async def send_test(req: SendTestReq) -> SendTestResp:
        try:
            uid = UUID(req.user_id)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid_user_id",
            ) from exc
        channel = Channel(req.channel) if req.channel else Channel.EMAIL
        payload = req.payload or "test notification"
        n = await svc.send(uid, channel, payload)
        return SendTestResp(
            notification_id=str(n.id),
            channel=str(n.channel),
            sent_at=n.sent_at,
        )

    return router
