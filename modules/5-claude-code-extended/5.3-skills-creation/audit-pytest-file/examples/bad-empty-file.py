"""bad-empty-file.py — a test file with no test functions.

The file imports things and even defines helpers, but nothing matches pytest's
discovery rules (`test_*` functions, `Test*` classes). The audit should emit
category=collection severity=warning saying no tests were collected.
"""

VERSION = "0.1.0"


def helper(x: int) -> int:
    return x * 2
