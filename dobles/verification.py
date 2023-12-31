from inspect import isbuiltin, isfunction, ismethod, signature

from dobles.exceptions import (
    VerifyingBuiltinDoubleArgumentError,
    VerifyingDoubleArgumentError,
    VerifyingDoubleError,
)

ACCEPTS_ARGS = (list, tuple, set)
ACCEPTS_KWARGS = (dict,)

SELF_OR_CLASS = "SELF_OR_CLASS"


def _is_python_function(func):
    if ismethod(func):
        func = func.__func__
    return isfunction(func)


def is_callable(obj):
    if isfunction(obj):
        return True
    return hasattr(obj, "__call__")


def _verify_arguments_of_dobles__new__(target, args, kwargs):
    """Verify arg/kwargs against a class's __init__

    :param class target: The class to verify against.
    :param tuple args:  Positional arguments.
    :params dict kwargs: Keyword arguments.
    """
    if not _is_python_function(target.doubled_obj.__init__):
        class_ = target.doubled_obj
        if args and not kwargs and issubclass(class_, ACCEPTS_ARGS):
            return True
        elif kwargs and not args and issubclass(class_, ACCEPTS_KWARGS):
            return True
        elif args or kwargs:
            given_args_count = 1 + len(args) + len(kwargs)
            raise VerifyingDoubleArgumentError(
                "__init__() takes exactly 1 arguments ({} given)".format(
                    given_args_count,
                )
            )
        return

    return _verify_arguments(
        target.doubled_obj.__init__,
        "__init__",
        [SELF_OR_CLASS] + list(args),
        kwargs,
    )


def _raise_dobles_error_from_index_error(method_name):
    # Work Around for http://bugs.python.org/issue20817
    raise VerifyingDoubleArgumentError(
        "{method}() missing 3 or more arguments.".format(method=method_name)
    )


def verify_method(target, method_name, class_level=False):
    """Verifies that the provided method exists on the target object.

    :param Target target: A ``Target`` object containing the object with the method to double.
    :param str method_name: The name of the method to double.
    :raise: ``VerifyingDoubleError`` if the attribute doesn't exist, if it's not a callable object,
        and in the case where the target is a class, that the attribute isn't an instance method.
    """

    attr = target.get_attr(method_name)

    if not attr:
        raise VerifyingDoubleError(method_name, target.doubled_obj).no_matching_method()

    if (
        attr.kind == "data"
        and not isbuiltin(attr.object)
        and not is_callable(attr.object)
    ):
        raise VerifyingDoubleError(method_name, target.doubled_obj).not_callable()

    if class_level and attr.kind == "method" and method_name != "__new__":
        raise VerifyingDoubleError(method_name, target.doubled_obj).requires_instance()


def verify_arguments(target, method_name, args, kwargs):
    """Verifies that the provided arguments match the signature of the provided method.

    :param Target target: A ``Target`` object containing the object with the method to double.
    :param str method_name: The name of the method to double.
    :param tuple args: The positional arguments the method should be called with.
    :param dict kwargs: The keyword arguments the method should be called with.
    :raise: ``VerifyingDoubleError`` if the provided arguments do not match the signature.
    """

    if method_name == "_dobles__new__":
        return _verify_arguments_of_dobles__new__(target, args, kwargs)

    attr = target.get_attr(method_name)
    method = attr.object

    if attr.kind in (
        "data",
        "attribute",
        "toplevel",
        "class method",
        "static method",
    ):
        try:
            if isinstance(method, (classmethod, staticmethod)):
                method = method.__get__(None, (attr.defining_class))
        except AttributeError:
            method = method.__call__
    elif attr.kind == "property":
        if args or kwargs:
            raise VerifyingDoubleArgumentError("Properties do not accept arguments.")
        return
    else:
        args = [SELF_OR_CLASS] + list(args)

    _verify_arguments(method, method_name, args, kwargs)


def _verify_arguments(method, method_name, args, kwargs):
    try:
        signature(method).bind(*args, **kwargs)
    except ValueError as e:
        raise VerifyingBuiltinDoubleArgumentError(str(e))
    except TypeError as e:
        raise VerifyingDoubleArgumentError(str(e))
