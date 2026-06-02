"""Контракт для to_markdown (story SNIP-5).

На чистому checkout усі ці тести ЧЕРВОНІ: export.py - заглушка з
NotImplementedError. Тести - незмінний контракт: правильна реалізація робить
їх зеленими, не навпаки.
"""

from snippets.models import Snippet
from snippets.export import to_markdown


def test_to_markdown_basic_structure():
    md = to_markdown(Snippet(id="a", title="Hi", body="print(1)", language="python", tags=["py"]))
    assert md == "## Hi\n```python\nprint(1)\n```\nТеги: py"


def test_to_markdown_joins_multiple_tags_with_comma_space():
    md = to_markdown(Snippet(id="a", title="T", body="x", language="text", tags=["a", "b", "c"]))
    assert md == "## T\n```text\nx\n```\nТеги: a, b, c"


def test_to_markdown_no_tags_renders_dash():
    md = to_markdown(Snippet(id="a", title="T", body="x", language="text"))
    assert md == "## T\n```text\nx\n```\nТеги: -"


def test_to_markdown_starts_with_h2_title():
    md = to_markdown(Snippet(id="a", title="Async", body="await", language="python", tags=[]))
    assert md.splitlines()[0] == "## Async"


def test_to_markdown_uses_language_in_fence():
    md = to_markdown(Snippet(id="a", title="T", body="SELECT 1", language="sql", tags=["db"]))
    lines = md.splitlines()
    assert lines[1] == "```sql"
    assert lines[3] == "```"
