"""Сховище сніпетів у памʼяті. Готовий substrate - конкретна зелена ціль для /loop."""

from __future__ import annotations

from uuid import uuid4

from snippets.models import Snippet


class SnippetStore:
    """Просте сховище сніпетів у памʼяті.

    Призначення в демо - бути зеленою ціллю, яку `make verify` (а через нього
    `/loop`-рецепт) опитує. Жодної бізнес-логіки тут немає навмисно.
    """

    def __init__(self) -> None:
        self._items: dict[str, Snippet] = {}

    def add(self, snippet: Snippet) -> str:
        """Зберегти сніпет і повернути його id.

        Якщо id порожній - згенерувати новий через uuid4().hex і проставити
        його у сам обʼєкт перед збереженням.
        """
        if not snippet.id:
            snippet.id = uuid4().hex
        self._items[snippet.id] = snippet
        return snippet.id

    def get(self, snippet_id: str) -> Snippet | None:
        """Повернути сніпет за id або None, якщо такого немає."""
        return self._items.get(snippet_id)

    def all(self) -> list[Snippet]:
        """Повернути всі збережені сніпети у порядку додавання."""
        return list(self._items.values())
