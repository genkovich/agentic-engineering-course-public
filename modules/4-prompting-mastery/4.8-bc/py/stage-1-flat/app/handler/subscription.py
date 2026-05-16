from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repository.subscription import SubscriptionRepo
from app.service.subscription import SubscriptionService

router = APIRouter(tags=["billing"])


class SubscribeReq(BaseModel):
    user_id: str
    plan: str


class SubscribeResp(BaseModel):
    subscription_id: str
    plan: str
    next_charge_at: datetime


@router.post(
    "/subscriptions",
    status_code=status.HTTP_201_CREATED,
    response_model=SubscribeResp,
)
async def subscribe(
    req: SubscribeReq, session: AsyncSession = Depends(get_session)
) -> SubscribeResp:
    if not req.plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_request"
        )
    try:
        uid = UUID(req.user_id)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_user_id"
        ) from exc
    svc = SubscriptionService(SubscriptionRepo(session))
    sub = await svc.subscribe(uid, req.plan)
    return SubscribeResp(
        subscription_id=str(sub.id), plan=sub.plan, next_charge_at=sub.next_charge_at
    )
