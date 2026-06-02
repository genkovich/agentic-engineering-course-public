"""Тести експорту в Markdown (SNIP-5). RED на чистому checkout: export.py = NotImplementedError."""

from snippets.models import Snippet
from snippets.export import to_markdown


def test_to_markdown_has_heading_and_fenced_block():
    s = Snippet(id="1", title="Read file", body="open(path)", language="python", tags=["python", "io"])
    md = to_markdown(s)
    assert md == (
        "## Read file\n"
        "```python\n"
        "open(path)\n"
        "```\n"
        "Теги: python, io"
    )


def test_to_markdown_default_language_is_text():
    s = Snippet(id="2", title="Note", body="hello")
    md = to_markdown(s)
    assert "```text\n" in md
    assert md.startswith("## Note\n")


def test_to_markdown_no_tags_line_is_empty_list():
    s = Snippet(id="3", title="Empty", body="x", language="bash")
    md = to_markdown(s)
    assert md.endswith("Теги: ")
