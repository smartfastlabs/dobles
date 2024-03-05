import pytest

from dobles.lifecycle import teardown, verify


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    outcome = yield

    try:
        outcome.get_result()
        try:
            verify()
        except Exception as e:
            outcome.force_exception(e)
    finally:
        teardown()
