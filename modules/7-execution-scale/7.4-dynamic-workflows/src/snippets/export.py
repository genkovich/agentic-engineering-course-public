"""Експорт сніпета у Markdown.

Це ЗАГЛУШКА (story SNIP-5). Функція піднімає NotImplementedError - `pytest`
на чистому checkout червоний навмисно. Це один з трьох НЕЗАЛЕЖНИХ файлів
(search.py / dedupe.py / export.py), які workflow реалізує паралельно: цей агент
пише рівно у export.py і не торкається ні search.py, ні dedupe.py.

Контракт описаний у docstring і в tasks/story-snip-5.md.
"""

from __future__ import annotations

from snippets.models import Snippet


def to_markdown(snippet: Snippet) -> str:
    """Відрендерити сніпет у секцію Markdown.

    Формат (рядки розділені '\\n'):
        ## {title}
        ```{language}
        {body}
        ```
        Теги: tag1, tag2

    Деталі:
        - Заголовок другого рівня з title сніпета.
        - Огороджений блок коду (fenced code block) з мовою з language і вмістом body.
        - Останній рядок "Теги: ..." з тегами через ", ". Якщо тегів немає -
          рядок "Теги: -".

    Приклад для Snippet(title="Hi", body="print(1)", language="python", tags=["py"]):
        ## Hi
        ```python
        print(1)
        ```
        Теги: py
    """
    raise NotImplementedError("to_markdown is story SNIP-5 - implement per docstring")
