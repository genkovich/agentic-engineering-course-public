"""Нормалізація тегів. Працює - це залежність search.py, не сама задача.

`search_by_tag` зі search.py звіряє теги у нормалізованій формі, тож нормалізація
має бути готовою заздалегідь. Реалізована тут навмисно - щоб задача SNIP-3 (search)
залишалась рівно про пошук, а не тягла ще й нормалізацію.
"""

from __future__ import annotations

import re

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


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
    collapsed = _NON_ALNUM.sub("-", raw.strip().lower())
    return collapsed.strip("-")
