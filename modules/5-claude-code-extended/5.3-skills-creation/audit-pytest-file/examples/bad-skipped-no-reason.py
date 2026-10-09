"""bad-skipped-no-reason.py — every test marked skip with no explanation.

The audit should report category=skipped severity=warning saying every test in
the file was skipped (the file produces no signal). Fix: drop the markers, or
add a reason explaining why.
"""
import pytest


@pytest.mark.skip
def test_first_thing():
    assert False, "would fail if we ran it, but we don't"


@pytest.mark.skip
def test_second_thing():
    assert False, "same story"
