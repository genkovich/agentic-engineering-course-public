"""FastAPI entrypoint — wires every BC feature module.

Vertical slice: each BC lives under ``app/features/<bc>/`` and exposes a router.
"""
from __future__ import annotations

from fastapi import FastAPI

from app.features.auth.handler import router as auth_router
from app.features.billing.handler import router as billing_router
from app.features.catalog.handler import router as catalog_router
from app.features.commerce.handler import router as commerce_router
from app.features.notifications.handler import router as notifications_router

app = FastAPI(title="stage-2-feature-first")

app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(commerce_router)
app.include_router(billing_router)
app.include_router(notifications_router)


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}
