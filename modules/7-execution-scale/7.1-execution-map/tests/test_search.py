"""Тести пошуку (SNIP-3). RED на чистому checkout: search.py = NotImplementedError."""

from snippets.models import Snippet
from snippets.search import search_by_tag, search_by_text

SNIPPETS = [
    Snippet(id="1", title="Read file", body="open(path)", language="python", tags=["python", "io"]),
    Snippet(id="2", title="HTTP GET", body="requests.get(url)", language="python", tags=["http"]),
    Snippet(id="3", title="Slugify", body="text.lower()", language="python", tags=["Python"]),
]


def test_search_by_tag_matches_normalized():
    ids = [s.id for s in search_by_tag(SNIPPETS, "PYTHON")]
    assert ids == ["1", "3"]


def test_search_by_tag_no_match():
    assert search_by_tag(SNIPPETS, "rust") == []


def test_search_by_text_matches_title_or_body():
    ids = [s.id for s in search_by_text(SNIPPETS, "get")]
    assert ids == ["2"]


def test_search_by_text_is_case_insensitive():
    ids = [s.id for s in search_by_text(SNIPPETS, "FILE")]
    assert ids == ["1"]
