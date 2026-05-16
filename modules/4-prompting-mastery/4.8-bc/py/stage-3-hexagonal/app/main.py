"""FastAPI entrypoint — wires every BC module via self-registering router builders.

Each BC has a ``module.py`` that returns a ``Module`` with a ``routes()`` method
returning a FastAPI ``APIRouter``. ``main`` does not import BC internals — it
only knows the public ``Module`` API. This keeps ``main`` open for extension:
add a new BC, add ``app.<bc>.module.New(...)`` to the list — done.
"""
from __future__ import annotations

from fastapi import FastAPI

from app.auth import module as auth_module
from app.billing import module as billing_module
from app.catalog import module as catalog_module
from app.commerce import module as commerce_module
from app.notifications import module as notifications_module
from app.shared.db import SessionMaker
from app.shared.events import EventBus

app = FastAPI(title="stage-3-hexagonal")
bus = EventBus()


def _build_modules() -> list[object]:
    return [
        auth_module.New(SessionMaker, bus),
        catalog_module.New(SessionMaker),
        commerce_module.New(SessionMaker, bus),
        billing_module.New(SessionMaker, bus),
        notifications_module.New(SessionMaker, bus),
    ]


for mod in _build_modules():
    app.include_router(mod.routes())  # type: ignore[attr-defined]


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}
