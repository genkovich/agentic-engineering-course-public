"""Тести нормалізації тегів (SNIP-2). RED на чистому checkout: tags.py = NotImplementedError."""

from snippets.models import Snippet
from snippets.tags import count_by_tag, normalize_tag


def test_normalize_lowercases_and_trims():
    assert normalize_tag("  Python  ") == "python"


def test_normalize_collapses_non_alnum_runs():
    assert normalize_tag("Python 3.12") == "python-3-12"


def test_normalize_trims_edge_dashes():
    assert normalize_tag("--Go--") == "go"


def test_count_by_tag_uses_normalized_form():
    snippets = [
        Snippet(id="1", title="a", body="x", tags=["Python", "go"]),
        Snippet(id="2", title="b", body="y", tags=["python", "  GO  "]),
    ]
    assert count_by_tag(snippets) == {"python": 2, "go": 2}
