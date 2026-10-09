"""bad-errored-fixture.py — a fixture raises during setup.

The audit should report category=fixture severity=error for the dependent
test (setup failed before the test body could run).
"""
import pytest


@pytest.fixture
def broken_resource():
    raise RuntimeError("connection to imaginary database refused")


def test_uses_broken_fixture(broken_resource):
    assert broken_resource is not None
