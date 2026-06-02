"""Failing-by-design test for the Ralph loop demo (Lecture 7.2).

On a clean checkout `app/` does not exist, so the import below raises
ModuleNotFoundError — this is the red state the first Ralph iteration sees.
Ralph must create `app/text_utils.py` so these cases turn green.
"""

from app.text_utils import slugify


def test_basic_slug():
    assert slugify("Hello World") == "hello-world"


def test_strip_punctuation_and_collapse():
    assert slugify("Hello,   World!!!") == "hello-world"


def test_trim_edges():
    assert slugify("--Hi--") == "hi"


def test_digits_kept():
    assert slugify("Top 10 Tips") == "top-10-tips"


def test_empty_string():
    assert slugify("") == ""
