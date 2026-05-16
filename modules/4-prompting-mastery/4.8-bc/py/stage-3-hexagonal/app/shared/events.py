"""Minimal in-memory event bus for cross-BC communication.

Publishers do not know about subscribers. Subscribers register handlers
in their own ``infra/events/`` package. The bus dispatches events
synchronously; ``async`` handlers are awaited.
"""
from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any


class Event:
    """Base event marker. Subclasses inherit ``name()`` classmethod."""

    @classmethod
    def name(cls) -> str:
        return f"{cls.__module__}.{cls.__name__}"


Handler = Callable[[Event], Awaitable[None] | None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._handlers.setdefault(event_name, []).append(handler)

    async def publish(self, event: Event) -> None:
        handlers = list(self._handlers.get(event.name(), []))
        for h in handlers:
            result: Any = h(event)
            if inspect.isawaitable(result):
                await result
