"""bad-slow-test.py — a test that calls time.sleep, exceeding 0.5s threshold.

The audit should report category=slow severity=warning for this test.
The fix is to mock time, parametrize fast equivalents, or move the test out of
the unit suite.
"""
import time


def test_fast_passes_threshold():
    assert sum(range(100)) == 4950


def test_slow_sleeps_for_real():
    time.sleep(0.7)
    assert True
