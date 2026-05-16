from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.commerce.repository import Repository
from app.features.commerce.service import Service
from app.shared.db import get_session

router = APIRouter(tags=["commerce"])


class PlaceReq(BaseModel):
    user_id: str
    total_cents: int


class PlaceResp(BaseModel):
    order_id: str
    status: str


@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=PlaceResp)
async def place_order(
    req: PlaceReq, session: AsyncSession = Depends(get_session)
) -> PlaceResp:
    try:
        uid = UUID(req.user_id)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_user_id"
        ) from exc
    svc = Service(Repository(session))
    o = await svc.place(uid, req.total_cents)
    return PlaceResp(order_id=str(o.id), status=o.status)
