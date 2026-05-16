from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.repository import Repository
from app.features.auth.service import InvalidCredentialsError, Service
from app.shared.db import get_session

router = APIRouter(tags=["auth"])


class CredsReq(BaseModel):
    email: EmailStr
    password: str


class UserResp(BaseModel):
    user_id: str
    email: str


@router.post(
    "/auth/register", status_code=status.HTTP_201_CREATED, response_model=UserResp
)
async def register(
    req: CredsReq, session: AsyncSession = Depends(get_session)
) -> UserResp:
    if not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_request"
        )
    svc = Service(Repository(session))
    u = await svc.register(req.email, req.password)
    return UserResp(user_id=str(u.id), email=u.email)


@router.post("/auth/login", response_model=UserResp)
async def login(
    req: CredsReq, session: AsyncSession = Depends(get_session)
) -> UserResp:
    svc = Service(Repository(session))
    try:
        u = await svc.login(req.email, req.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        ) from exc
    return UserResp(user_id=str(u.id), email=u.email)
