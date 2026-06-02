"""Контракт для normalize_tag і count_by_tag.

На чистому checkout усі ці тести ЧЕРВОНІ: tags.py - заглушка з
NotImplementedError. Це стартовий стан задачі, яку доводить до завершення
`/goal` (умова закривається, коли тут усе зелене). Тести - незмінний контракт:
правильна реалізація робить їх зеленими, не навпаки.
"""

from snippets.models import Snippet
from snippets.tags import count_by_tag, normalize_tag


def test_normalize_basic_lowercase_and_space():
    # "  Hello World " → strip, lower, пробіл → один дефіс.
    assert normalize_tag("  Hello World ") == "hello-world"


def test_normalize_collapses_runs_of_non_alphanumeric():
    # Кратні роздільники й пунктуація схлопуються в один дефіс.
    assert normalize_tag("Python,   3.12!!!") == "python-3-12"


def test_normalize_trims_leading_and_trailing_dashes():
    # Дефіси з країв прибираються; "C++" → "c" (++ це край).
    assert normalize_tag("--Hi--") == "hi"
    assert normalize_tag("C++") == "c"


def test_normalize_is_idempotent():
    # Вже нормалізований тег не змінюється повторним проганянням.
    once = normalize_tag("Hello World!")
    assert normalize_tag(once) == once == "hello-world"


def test_count_by_tag_groups_normalized_variants_together():
    # Різні написання того самого тегу мають злитись в один ключ.
    snippets = [
        Snippet(id="a", title="A", body="...", tags=["Python", "python "]),
        Snippet(id="b", title="B", body="...", tags=["PYTHON"]),
        Snippet(id="c", title="C", body="...", tags=["go"]),
    ]
    counts = count_by_tag(snippets)
    assert counts == {"python": 3, "go": 1}


def test_count_by_tag_drops_empty_normalized_tag():
    # Тег, що нормалізується в порожній рядок ("!!!"), у результат не потрапляє.
    snippets = [
        Snippet(id="a", title="A", body="...", tags=["!!!", "Edge Case"]),
    ]
    counts = count_by_tag(snippets)
    assert counts == {"edge-case": 1}


def test_count_by_tag_empty_input_is_empty_dict():
    assert count_by_tag([]) == {}
