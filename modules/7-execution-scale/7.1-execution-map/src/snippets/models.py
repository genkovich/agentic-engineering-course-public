"""Доменна модель сніпета. Це єдиний WORKING-модуль на чистому checkout."""

from dataclasses import dataclass, field


@dataclass
class Snippet:
    """Один код-сніпет.

    Поля:
        id: ідентифікатор. Порожній рядок означає «ще не збережений»
            (SnippetStore призначить uuid4 при додаванні).
        title: людський заголовок.
        body: тіло сніпета (код або текст).
        language: мова для підсвітки, дефолт "text".
        tags: список тегів (нормалізуються в модулі tags).
    """

    id: str
    title: str
    body: str
    language: str = "text"
    tags: list[str] = field(default_factory=list)
