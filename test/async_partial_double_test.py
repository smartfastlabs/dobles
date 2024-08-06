import pytest
from pytest import raises

import dobles.testing
from dobles import allow
from dobles.exceptions import (
    UnallowedMethodCallError,
    VerifyingDoubleArgumentError,
    VerifyingDoubleError,
)
from dobles.lifecycle import teardown
from dobles.testing import AsyncUser


class TestAsyncInstanceMethods(object):
    @pytest.mark.asyncio
    async def test_arbitrary_callable_on_instance(self):
        instance = AsyncUser("Bob", 10)
        allow(instance).arbitrary_callable.and_return("Bob Barker", "Drew Carey")
        assert (await instance.arbitrary_callable()) == "Bob Barker"
        assert (await instance.arbitrary_callable()) == "Drew Carey"
        assert (await instance.arbitrary_callable()) == "Drew Carey"
        teardown()
        assert (await instance.arbitrary_callable()) == "ArbitraryCallable Value"

    @pytest.mark.asyncio
    async def test_arbitrary_callable_on_instance_and_return_result(self):
        instance = AsyncUser("Bob", 10)
        allow(instance).arbitrary_callable.and_return_result_of(lambda *_: "Bob Barker")
        assert (await instance.arbitrary_callable()) == "Bob Barker"
        teardown()
        assert (await instance.arbitrary_callable()) == "ArbitraryCallable Value"

    @pytest.mark.asyncio
    async def test_arbitrary_callable_on_class(self):
        allow(AsyncUser).arbitrary_callable.and_return("Bob Barker")
        assert (await AsyncUser.arbitrary_callable()) == "Bob Barker"
        teardown()
        assert (await AsyncUser.arbitrary_callable()) == "ArbitraryCallable Value"

    @pytest.mark.asyncio
    async def test_callable_class_attribute(self):
        allow(AsyncUser).callable_class_attribute.and_return("Bob Barker")
        assert (await AsyncUser.callable_class_attribute()) == "Bob Barker"
        teardown()
        assert (await AsyncUser.callable_class_attribute()) == "dummy result"

    @pytest.mark.asyncio
    async def test_callable_instance_attribute(self):
        user = AsyncUser("Alice", 25)
        allow(user).callable_instance_attribute.and_return("Bob Barker")

        assert (await user.callable_instance_attribute()) == "Bob Barker"
        teardown()
        assert (await user.callable_instance_attribute()) == "dummy result"

    @pytest.mark.asyncio
    async def test_stubs_instance_methods(self):
        user = AsyncUser("Alice", 25)

        allow(user).get_name.and_return("Bob")

        assert (await user.get_name()) == "Bob"

    @pytest.mark.asyncio
    async def test_restores_instance_methods_on_teardown(self):
        user = AsyncUser("Alice", 25)
        allow(user).get_name.and_return("Bob")

        teardown()

        assert (await user.get_name()) == "Alice"

    @pytest.mark.asyncio
    async def test_only_affects_stubbed_method(self):
        user = AsyncUser("Alice", 25)

        allow(user).get_name.and_return("Bob")

        assert user.age == 25

    @pytest.mark.asyncio
    async def test_raises_when_stubbing_nonexistent_methods(self):
        user = AsyncUser("Alice", 25)

        with raises(VerifyingDoubleError):
            allow(user).gender


class TestAsync__call__(object):
    @pytest.mark.asyncio
    async def test_basic_usage(self):
        user = AsyncUser("Alice", 25)
        allow(user).__call__.and_return("bob barker")

        assert (await user()) == "bob barker"

    @pytest.mark.asyncio
    async def test_stubbing_two_objects_does_not_interfere(self):
        alice = AsyncUser("Alice", 25)
        peter = AsyncUser("Peter", 25)

        allow(alice).__call__.and_return("alice")
        allow(peter).__call__.and_return("peter")

        assert (await alice()) == "alice"
        assert (await peter()) == "peter"

    @pytest.mark.asyncio
    async def test_works_with_arguments(self):
        user = AsyncUser("Alice", 25)
        allow(user).__call__.with_args(1, 2).and_return("bob barker")

        assert (await user(1, 2)) == "bob barker"

    @pytest.mark.asyncio
    async def test_raises_when_called_with_invalid_args(self):
        user = AsyncUser("Alice", 25)
        allow(user).__call__.with_args(1, 2).and_return("bob barker")

        with raises(UnallowedMethodCallError):
            await user(1, 2, 3)

    @pytest.mark.asyncio
    async def test_raises_when_mocked_with_invalid_call_signature(self):
        user = AsyncUser("Alice", 25)
        with raises(VerifyingDoubleArgumentError):
            await allow(user).__call__.with_args(1, 2, bob="barker")


class TestAsync__aenter__(object):
    # TODO: What do I need to do here
    @pytest.mark.asyncio
    async def test_basic_usage(self):
        user = AsyncUser("Alice", 25)
        allow(user).__aenter__.and_return(user)

        async with user as u:
            assert user == u

    @pytest.mark.asyncio
    async def test_stubbing_two_objects_does_not_interfere(self):
        alice = AsyncUser("Alice", 25)
        bob = AsyncUser("Bob", 25)

        allow(alice).__aenter__.and_return("alice")
        allow(bob).__aenter__.and_return("bob")

        async with alice as a:
            assert a == "alice"

        async with bob as b:
            assert b == "bob"

    @pytest.mark.asyncio
    async def test_does_not_intefere_with_unstubbed_objects(self):
        alice = AsyncUser("Alice", 25)
        bob = AsyncUser("Bob", 25)

        allow(alice).__aenter__.and_return("user")

        async with alice as a:
            assert a == "user"

        async with bob as b:
            assert b == bob

    @pytest.mark.asyncio
    async def test_teardown_restores_previous_functionality(self):
        user = AsyncUser("Alice", 25)
        allow(user).__aenter__.and_return("bob barker")

        async with user as u:
            assert u == "bob barker"

        teardown()

        async with user as u:
            assert u == user

    @pytest.mark.asyncio
    async def test_raises_when_mocked_with_invalid_call_signature(self):
        user = AsyncUser("Alice", 25)
        with raises(VerifyingDoubleArgumentError):
            allow(user).__aenter__.with_args(1)


class TestAsync__aexit__(object):
    @pytest.mark.asyncio
    async def test_basic_usage(self):
        user = AsyncUser("Alice", 25)
        allow(user).__aexit__.with_args(None, None, None)

        async with user:
            pass

    @pytest.mark.asyncio
    async def test_stubbing_two_objects_does_not_interfere(self):
        alice = AsyncUser("Alice", 25)
        bob = AsyncUser("Bob", 25)

        allow(alice).__aexit__.and_return("alice")
        allow(bob).__aexit__.and_return("bob")

        assert (await alice.__aexit__(None, None, None)) == "alice"
        assert (await bob.__aexit__(None, None, None)) == "bob"

    @pytest.mark.asyncio
    async def test_does_not_intefere_with_unstubbed_objects(self):
        alice = AsyncUser("Alice", 25)
        bob = AsyncUser("Bob", 25)

        allow(alice).__aexit__.and_return("user")

        assert (await alice.__aexit__(None, None, None)) == "user"
        assert (await bob.__aexit__(None, None, None)) is None

    @pytest.mark.asyncio
    async def test_teardown_restores_previous_functionality(self):
        user = AsyncUser("Alice", 25)
        allow(user).__aexit__.and_return("bob barker")

        assert (await user.__aexit__(None, None, None)) == "bob barker"

        teardown()

        assert (await user.__aexit__(None, None, None)) is None

    @pytest.mark.asyncio
    async def test_raises_when_mocked_with_invalid_call_signature(self):
        user = AsyncUser("Alice", 25)
        with raises(VerifyingDoubleArgumentError):
            allow(user).__aexit__.with_no_args()


class TestAsyncClassMethods(object):
    @pytest.mark.asyncio
    async def test_stubs_class_methods(self):
        allow(AsyncUser).class_method.with_args("foo").and_return("overridden value")

        assert (await AsyncUser.class_method("foo")) == "overridden value"

    @pytest.mark.asyncio
    async def test_restores_class_methods_on_teardown(self):
        allow(AsyncUser).class_method.and_return("overridden value")

        teardown()

        assert (await AsyncUser.class_method("foo")) == "class_method return value: foo"

    @pytest.mark.asyncio
    async def test_raises_when_stubbing_noncallable_attributes(self):
        with raises(VerifyingDoubleError):
            allow(AsyncUser).class_attribute

    @pytest.mark.asyncio
    async def test_raises_when_stubbing_nonexistent_class_methods(self):
        with raises(VerifyingDoubleError):
            allow(AsyncUser).nonexistent_method


class TestTopLevelFunctions(object):
    @pytest.mark.asyncio
    async def test_stubs_method(self):
        allow(dobles.testing).async_top_level_function.and_return("foo")

        assert (await dobles.testing.async_top_level_function("bob barker")) == "foo"

    @pytest.mark.asyncio
    async def test_restores_the_orignal_method(self):
        allow(dobles.testing).async_top_level_function.and_return("foo")
        teardown()
        assert (
            await dobles.testing.async_top_level_function("foo", "bar")
        ) == "foo -- bar"

    @pytest.mark.asyncio
    async def test_raises_if_incorrect_call_signature_used(self):
        with raises(VerifyingDoubleArgumentError):
            allow(dobles.testing).async_top_level_function.with_args(
                "bob", "barker", "is_great"
            )

    @pytest.mark.asyncio
    async def test_allows_correct_call_signature(self):
        allow(dobles.testing).async_top_level_function.with_args(
            "bob",
            "barker",
        ).and_return("bar")
        # assert (await dobles.testing.async_top_level_function("bob", "barker")) == "bar"

    @pytest.mark.asyncio
    async def test_verifies_the_function_exists(self):
        with raises(VerifyingDoubleError):
            allow(dobles.testing).fake_function

    @pytest.mark.asyncio
    async def test_callable_top_level_variable(self):
        allow(dobles.testing).async_callable_variable.and_return("foo")

        assert (await dobles.testing.async_callable_variable("bob barker")) == "foo"

    @pytest.mark.asyncio
    async def test_decorated_function(self):
        allow(dobles.testing).async_decorated_function_callable.and_return("foo")

        assert (
            await dobles.testing.async_decorated_function_callable("bob barker")
        ) == "foo"

    @pytest.mark.asyncio
    async def test_decorated_function_that_returns_a_callable(self):
        allow(dobles.testing).async_decorated_function_callable.and_return("foo")

        assert (
            await dobles.testing.async_decorated_function_callable("bob barker")
        ) == "foo"

    @pytest.mark.asyncio
    async def test_variable_that_points_to_class_method(self):
        allow(dobles.testing).async_class_method("bob barker").and_return("foo")

        assert (await dobles.testing.async_class_method("bob barker")) == "foo"

    @pytest.mark.asyncio
    async def test_variable_that_points_to_instance_method(self):
        allow(dobles.testing).async_instance_method.and_return("foo")

        assert (await dobles.testing.async_instance_method()) == "foo"
