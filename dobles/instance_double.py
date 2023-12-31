from inspect import isclass

from dobles.exceptions import VerifyingDoubleImportError
from dobles.object_double import ObjectDouble
from dobles.utils import get_module, get_path_components


def _get_dobles_target(module, class_name, path):
    """Validate and return the class to be doubled.

    :param module module: The module that contains the class that will be doubled.
    :param str class_name: The name of the class that will be doubled.
    :param str path: The full path to the class that will be doubled.
    :return: The class that will be doubled.
    :rtype: type
    :raise: ``VerifyingDoubleImportError`` if the target object doesn't exist or isn't a class.
    """

    try:
        dobles_target = getattr(module, class_name)
        if isinstance(dobles_target, ObjectDouble):
            return dobles_target._dobles_target

        if not isclass(dobles_target):
            raise VerifyingDoubleImportError(
                "Path does not point to a class: {}.".format(path)
            )

        return dobles_target
    except AttributeError:
        raise VerifyingDoubleImportError("No object at path: {}.".format(path))


class InstanceDouble(ObjectDouble):
    """A pure double representing an instance of the target class.

    Any kwargs supplied will be set as attributes on the instance that is
    created.

    ::

        user = InstanceDouble('myapp.User', name='Bob Barker')

    :param str path: The absolute module path to the class.
    """

    def __init__(self, path, **kwargs):
        module_path, class_name = get_path_components(path)
        module = get_module(module_path, path)
        self._dobles_target = _get_dobles_target(module, class_name, path)
        for k, v in kwargs.items():
            setattr(self, k, v)
