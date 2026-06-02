"""Нормалізація тегів і підрахунок за тегом.

Це ЗАГЛУШКА. Обидві функції піднімають NotImplementedError - `pytest`
на чистому checkout червоний навмисно. Саме цю задачу `/goal` доводить до
завершення: умова закривається, коли всі тести в tests/test_tags.py зелені.

Контракт описаний у docstring кожної функції і в tasks/story-snip-2.md.
"""

from __future__ import annotations

from snippets.models import Snippet


def normalize_tag(raw: str) -> str:
    """Звести сирий тег до канонічної форми.

    Правила:
        1. Прибрати пробіли з країв (strip).
        2. Перевести у нижній регістр.
        3. Кожен непорожній прогін НЕ-алфанумерних символів замінити на один '-'.
        4. Прибрати дефіси з початку і кінця.

    Приклади:
        normalize_tag("  Hello World ")  == "hello-world"
        normalize_tag("C++")             == "c"
        normalize_tag("--Hi--")          == "hi"
        normalize_tag("foo")             == "foo"   # ідемпотентно
    """
    raise NotImplementedError("normalize_tag is the /goal task - implement per docstring")


def count_by_tag(snippets: list[Snippet]) -> dict[str, int]:
    """Порахувати, скільки сніпетів має кожен тег (після нормалізації).

    Кожен тег кожного сніпета проганяється через normalize_tag, далі
    рахується частота нормалізованих тегів. Порожній нормалізований тег
    (наприклад з рядка "!!!") до результату не потрапляє.

    Повертає dict {нормалізований_тег: кількість}.
    """
    raise NotImplementedError("count_by_tag is the /goal task - implement per docstring")
