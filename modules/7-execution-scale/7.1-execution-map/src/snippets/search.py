"""Пошук сніпетів за тегом і за текстом.

Рекомендований патерн: dynamic workflow (story SNIP-3).
SNIP-3 і SNIP-4 - незалежні підзадачі в різних файлах, тому їх можна
вести паралельними гілками dynamic workflow.

Контракт STUB - реалізації ще нема, усе кидає NotImplementedError.
"""

from snippets.models import Snippet


def search_by_tag(snippets: list[Snippet], tag: str) -> list[Snippet]:
    """Повернути сніпети, у яких є тег `tag`.

    Збіг рахується за нормалізованою формою тега (див. tags.normalize_tag):
    і шуканий `tag`, і теги сніпета нормалізуються перед порівнянням.
    Порядок результату - як у вхідному списку.
    """
    raise NotImplementedError("SNIP-3: search_by_tag ще не реалізовано")


def search_by_text(snippets: list[Snippet], q: str) -> list[Snippet]:
    """Повернути сніпети, де `q` зустрічається у title АБО body.

    Пошук без урахування регістру (case-insensitive підрядок).
    Порядок результату - як у вхідному списку.
    """
    raise NotImplementedError("SNIP-3: search_by_text ще не реалізовано")
