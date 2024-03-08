import pytest

from dobles.lifecycle import teardown, verify


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    try:
        outcome = yield
    except Exception as e:
        raise e
    finally:
        try:
            verify()
        except Exception as e:
            raise e
        finally:
            teardown()

    return outcome
