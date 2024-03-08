import pytest

from dobles.lifecycle import teardown, verify


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    try:
        outcome = yield
    finally:
        try:
            verify()
        finally:
            teardown()

    return outcome
