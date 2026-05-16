"""Commerce HTTP handler — POST /orders."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.commerce.app.service import Service
from app.commerce.domain.order import InvalidOrderError


class PlaceReq(BaseModel):
    user_id: str
    total_cents: int


class PlaceResp(BaseModel):
    order_id: str
    status: str


def build_router(svc: Service) -> APIRouter:
    router = APIRouter(tags=["commerce"])

    @router.post(
        "/orders",
        status_code=status.HTTP_201_CREATED,
        response_model=PlaceResp,
    )
    async def place_order(req: PlaceReq) -> PlaceResp:
        try:
            uid = UUID(req.user_id)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_user_id"
            ) from exc
        try:
            o = await svc.place(uid, req.total_cents)
        except InvalidOrderError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "commerce.invalid_order",
                    "message": "total_cents must be >= 0",
                },
            ) from exc
        return PlaceResp(order_id=str(o.id), status=o.status)

    return router
