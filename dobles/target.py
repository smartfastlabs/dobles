from collections import namedtuple
from inspect import (
    classify_class_attrs,
    getmembers,
    isclass,
    iscoroutinefunction,
    ismodule,
)
from typing import Any

from dobles.object_double import ObjectDouble
from dobles.verification import is_callable

Attribute = namedtuple("Attribute", ["object", "kind", "defining_class"])


def _proxy_class_method_to_instance(original, name):
    def func(instance, *args, **kwargs):
        if name in instance.__dict__:
            return instance.__dict__[name](*args, **kwargs)
        return original(instance, *args, **kwargs)

    func._dobles_target_method = original
    return func


class Target(object):
    """
    A wrapper around an object that owns methods to be doubled. Provides additional introspection
    such as the class and the kind (method, class, property, etc.)
    """

    def __init__(self, obj):
        """
        :param object obj: The real target object.
        """

        self.obj = obj
        self.doubled_obj = self._determine_doubled_obj()
        self.doubled_obj_type = self._determine_doubled_obj_type()
        self.attrs = self._generate_attrs()

    def is_class_or_module(self):
        """Determines if the object is a class or a module

        :return: True if the object is a class or a module, False otherwise.
        :rtype: bool
        """

        if isinstance(self.obj, ObjectDouble):
            return self.obj.is_class

        return isclass(self.doubled_obj) or ismodule(self.doubled_obj)

    def _determine_doubled_obj(self):
        """Return the target object.

        Returns the object that should be treated as the target object. For partial dobles, this
        will be the same as ``self.obj``, but for pure dobles, it's pulled from the special
        ``_dobles_target`` attribute.

        :return: The object to be doubled.
        :rtype: object
        """

        if isinstance(self.obj, ObjectDouble):
            return self.obj._dobles_target
        else:
            return self.obj

    def _determine_doubled_obj_type(self):
        """Returns the type (class) of the target object.

        :return: The type (class) of the target.
        :rtype: type, classobj
        """

        if isclass(self.doubled_obj) or ismodule(self.doubled_obj):
            return self.doubled_obj

        return self.doubled_obj.__class__

    def _generate_attrs(self):
        """Get detailed info about target object.

        Uses ``inspect.classify_class_attrs`` to get several important details about each attribute
        on the target object.

        :return: The attribute details dict.
        :rtype: dict
        """
        attrs = {}

        if ismodule(self.doubled_obj):
            for name, func in getmembers(self.doubled_obj, is_callable):
                attrs[name] = Attribute(func, "toplevel", self.doubled_obj)
        else:
            for attr in classify_class_attrs(self.doubled_obj_type):
                attrs[attr.name] = attr

        return attrs

    def hijack_attr(self, attr_name):
        """Hijack an attribute on the target object.

        Updates the underlying class and delegating the call to the instance.
        This allows specially-handled attributes like __call__, __enter__,
        and __exit__ to be mocked on a per-instance basis.

        :param str attr_name: the name of the attribute to hijack
        """
        if not self._original_attr(attr_name):
            setattr(
                self.obj.__class__,
                attr_name,
                _proxy_class_method_to_instance(
                    getattr(self.obj.__class__, attr_name, None), attr_name
                ),
            )

    def restore_attr(self, attr_name):
        """Restore an attribute back onto the target object.

        :param str attr_name: the name of the attribute to restore
        """
        original_attr = self._original_attr(attr_name)
        if self._original_attr(attr_name):
            setattr(self.obj.__class__, attr_name, original_attr)

    def _original_attr(self, attr_name):
        """Return the original attribute off of the proxy on the target object.

        :param str attr_name: the name of the original attribute to return
        :return: Func or None.
        :rtype: func
        """
        try:
            return getattr(
                getattr(self.obj.__class__, attr_name), "_dobles_target_method", None
            )
        except AttributeError:
            return None

    def get_callable_attr(self, attr_name):
        """Used to double methods added to an object after creation

        :param str attr_name: the name of the original attribute to return
        :return: Attribute or None.
        :rtype: func
        """

        if not hasattr(self.doubled_obj, attr_name):
            return None

        func = getattr(self.doubled_obj, attr_name)
        if not is_callable(func):
            return None

        attr = Attribute(
            func,
            "attribute",
            self.doubled_obj if self.is_class_or_module() else self.doubled_obj_type,
        )
        self.attrs[attr_name] = attr
        return attr

    def get_attr(self, method_name):
        """Get attribute from the target object"""
        return self.attrs.get(method_name) or self.get_callable_attr(method_name)

    def is_attr_async(self, name: str) -> bool:
        attr: Any = self.get_attr(name)
        object: Any = attr.object
        object = getattr(object, "_dobles_target_method", object)

        if iscoroutinefunction(object):
            return True

        if isinstance(object, classmethod):
            object = object.__get__(None, (attr.defining_class))

        else:
            for i in ("__call__", "__wrapped__"):
                if hasattr(object, i):
                    object = getattr(object, i)
                    break

        return iscoroutinefunction(object)
