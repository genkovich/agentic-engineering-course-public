"""Auth HTTP handler — POST /auth/register, POST /auth/login."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.auth.app.service import Service
from app.auth.domain.errors import AuthDomainError
from app.auth.infra.http.dto import (
    LoginReq,
    LoginResp,
    RegisterReq,
    RegisterResp,
)
from app.auth.infra.http.errors import to_app_error
from app.shared.httputil import to_http_exception


def build_router(svc: Service) -> APIRouter:
    router = APIRouter(tags=["auth"])

    @router.post(
        "/auth/register",
        status_code=status.HTTP_201_CREATED,
        response_model=RegisterResp,
    )
    async def register(req: RegisterReq) -> RegisterResp:
        if not req.password:
            raise HTTPException(status_code=400, detail="invalid_request")
        try:
            u = await svc.register(req.email, req.password)
        except AuthDomainError as exc:
            raise to_http_exception(to_app_error(exc)) from exc
        return RegisterResp(
            user_id=str(u.id), email=u.email, created_at=u.created_at
        )

    @router.post("/auth/login", response_model=LoginResp)
    async def login(req: LoginReq) -> LoginResp:
        try:
            u = await svc.login(req.email, req.password)
        except AuthDomainError as exc:
            raise to_http_exception(to_app_error(exc)) from exc
        return LoginResp(user_id=str(u.id), email=u.email)

    return router
