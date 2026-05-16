"""Notifications BC self-wiring.

Wires the repo, sender, service, event subscriber, and HTTP handler.
This is the only place where infra/postgres + infra/stub + infra/events +
infra/http meet — exactly as the layered ports/adapters pattern intends.
"""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.notifications.app.service import Service
from app.notifications.infra.events.subscriber import register as register_subs
from app.notifications.infra.http.handler import build_router
from app.notifications.infra.postgres.notification_repo import NotificationRepo
from app.notifications.infra.stub.sender import StubSender
from app.shared.events import EventBus


@dataclass
class Module:
    service: Service
    _router: APIRouter

    def routes(self) -> APIRouter:
        return self._router


def New(session_maker: async_sessionmaker, bus: EventBus) -> Module:
    repo = NotificationRepo(session_maker)
    sender = StubSender()
    svc = Service(repo, sender)
    register_subs(bus, svc)
    router = build_router(svc)
    return Module(service=svc, _router=router)
