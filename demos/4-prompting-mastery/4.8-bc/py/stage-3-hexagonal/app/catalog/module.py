"""Catalog BC self-wiring."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.catalog.app.service import Service
from app.catalog.infra.http.handler import build_router
from app.catalog.infra.postgres.product_repo import ProductRepo


@dataclass
class Module:
    service: Service
    _router: APIRouter

    def routes(self) -> APIRouter:
        return self._router


def New(session_maker: async_sessionmaker) -> Module:
    repo = ProductRepo(session_maker)
    svc = Service(repo)
    router = build_router(svc)
    return Module(service=svc, _router=router)
