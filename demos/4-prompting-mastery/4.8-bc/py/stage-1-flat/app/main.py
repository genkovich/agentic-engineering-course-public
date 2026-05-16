"""FastAPI entrypoint — wires every layer together.

Layered (handler/service/repository) without Bounded Contexts. BC exists
only in the team's heads — the file tree spreads functions across layers.
"""
from __future__ import annotations

from fastapi import FastAPI

from app.handler import notification, order, product, subscription, user

app = FastAPI(title="stage-1-flat")

app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(subscription.router)
app.include_router(notification.router)


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}
