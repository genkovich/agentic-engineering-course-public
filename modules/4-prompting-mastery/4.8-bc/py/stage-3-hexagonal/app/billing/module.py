"""Billing BC self-wiring."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.billing.app.service import Service
from app.billing.infra.http.handler import build_router
from app.billing.infra.postgres.subscription_repo import SubscriptionRepo
from app.shared.events import EventBus


@dataclass
class Module:
    service: Service
    _router: APIRouter

    def routes(self) -> APIRouter:
        return self._router


def New(session_maker: async_sessionmaker, bus: EventBus) -> Module:
    repo = SubscriptionRepo(session_maker)
    svc = Service(repo, bus)
    router = build_router(svc)
    return Module(service=svc, _router=router)
