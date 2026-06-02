"""Експорт сніпета у Markdown.

Рекомендований патерн: TDD (story SNIP-5).
Формат виводу - критична логіка з точними правилами; пишемо тест-першим,
щоб зафіксувати контракт до реалізації.

Контракт STUB - реалізації ще нема, усе кидає NotImplementedError.
"""

from snippets.models import Snippet


def to_markdown(snippet: Snippet) -> str:
    """Відрендерити сніпет як секцію Markdown.

    Формат (рядок за рядком):
        ## {title}
        ```{language}
        {body}
        ```
        Теги: {', '.join(tags)}

    Тобто: заголовок рівня 2, далі огороджений блок коду (fenced code
    block) з мовою сніпета і його тілом, далі рядок з тегами через
    кому-пробіл.
    """
    raise NotImplementedError("SNIP-5: to_markdown ще не реалізовано")
