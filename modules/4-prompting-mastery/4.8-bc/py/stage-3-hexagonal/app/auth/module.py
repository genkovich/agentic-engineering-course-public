"""Auth BC self-wiring — ``main.py`` calls ``New(SessionMaker, bus)``.

Returns a ``Module`` exposing only public surface: ``service`` and ``routes()``.
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.auth.app.service import Service
from app.auth.infra.http.handler import build_router
from app.auth.infra.postgres.user_repo import UserRepo
from app.shared.events import EventBus


@dataclass
class Module:
    service: Service
    _router: APIRouter

    def routes(self) -> APIRouter:
        return self._router


def New(session_maker: async_sessionmaker, bus: EventBus) -> Module:
    repo = UserRepo(session_maker)
    svc = Service(repo, bus)
    router = build_router(svc)
    return Module(service=svc, _router=router)
