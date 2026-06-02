"""Доменна модель сніпета. Працює - це готовий substrate, не задача."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Snippet:
    """Один збережений сніпет коду чи тексту.

    Поля:
        id:       стабільний ідентифікатор; порожній рядок означає «ще не збережений».
        title:    людиночитний заголовок.
        body:     власне вміст сніпета.
        language: мова підсвітки; за замовчуванням "text".
        tags:     теги сніпета.
    """

    id: str
    title: str
    body: str
    language: str = "text"
    tags: list[str] = field(default_factory=list)
