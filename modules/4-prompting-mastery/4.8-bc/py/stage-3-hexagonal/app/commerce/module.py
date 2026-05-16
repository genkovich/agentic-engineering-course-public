"""Commerce BC self-wiring."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.commerce.app.service import Service
from app.commerce.infra.http.handler import build_router
from app.commerce.infra.postgres.order_repo import OrderRepo
from app.shared.events import EventBus


@dataclass
class Module:
    service: Service
    _router: APIRouter

    def routes(self) -> APIRouter:
        return self._router


def New(session_maker: async_sessionmaker, bus: EventBus) -> Module:
    repo = OrderRepo(session_maker)
    svc = Service(repo, bus)
    router = build_router(svc)
    return Module(service=svc, _router=router)
