pytest_plugins = "pytester"


def test_exceptions_dont_cause_leaking_between_tests(pytester):
    pytester.makepyfile(
        """
        import pytest

        from dobles.targets.expectation_target import expect
        from dobles.testing import User

        def test_that_sets_expectation_then_raises():
            expect(User).class_method.with_args(1).once()
            raise Exception('Bob')

        @pytest.fixture
        def user():
            return "Bob Barker"

        def test_that_should_pass(user):
            assert True

    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, failed=1)


def test_failed_expections_do_not_leak_between_tests(pytester):
    pytester.makepyfile(
        """

        from dobles.targets.expectation_target import expect
        from dobles.testing import User

        def test_that_fails_for_not_satisfying_expectation():
            expect(User).class_method.with_args('test_one').once()

        def test_that_should_fail_for_not_satisfying_expection():
            expect(User).class_method.with_args('test_two').once()

        def test_that_should_pass():
            assert True

    """
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=2, passed=1)
    expected_error = (
        "*Expected 'class_method' to be called 1 time instead of 0 times on"
        " <class 'dobles.testing.User'> with ('{arg_value}')*"
    )
    result.stdout.fnmatch_lines([expected_error.format(arg_value="test_one")])
    result.stdout.fnmatch_lines([expected_error.format(arg_value="test_two")])
