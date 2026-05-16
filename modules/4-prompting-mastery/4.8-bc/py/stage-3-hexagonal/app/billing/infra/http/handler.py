"""Billing HTTP handler — POST /subscriptions."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.billing.app.service import Service
from app.billing.domain.subscription import InvalidPlanError


class SubscribeReq(BaseModel):
    user_id: str
    plan: str


class SubscribeResp(BaseModel):
    subscription_id: str
    plan: str
    next_charge_at: datetime


def build_router(svc: Service) -> APIRouter:
    router = APIRouter(tags=["billing"])

    @router.post(
        "/subscriptions",
        status_code=status.HTTP_201_CREATED,
        response_model=SubscribeResp,
    )
    async def subscribe(req: SubscribeReq) -> SubscribeResp:
        if not req.plan:
            raise HTTPException(status_code=400, detail="invalid_request")
        try:
            uid = UUID(req.user_id)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_user_id"
            ) from exc
        try:
            sub = await svc.subscribe(uid, req.plan)
        except InvalidPlanError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "billing.invalid_plan",
                    "message": "plan must be basic|pro|enterprise",
                },
            ) from exc
        return SubscribeResp(
            subscription_id=str(sub.id),
            plan=sub.plan,
            next_charge_at=sub.next_charge_at,
        )

    return router
