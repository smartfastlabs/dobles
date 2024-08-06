from importlib import import_module

from dobles.exceptions import VerifyingDoubleImportError


def get_module(module_path, full_path):
    """Return the module given its path.

    :param str module_path: The path to the module to import.
    :param str full_path: The full path to the class that will be doubled.
    :return: The module object.
    :rtype: module
    :raise: ``VerifyingDoubleImportError`` if the module can't be imported.
    """

    try:
        return import_module(module_path)
    except ImportError:
        raise VerifyingDoubleImportError(
            "Cannot import object from path: {}.".format(full_path)
        )


def get_path_components(path):
    """Extract the module name and class name out of the fully qualified path to the class.

    :param str path: The full path to the class.
    :return: The module path and the class name.
    :rtype: str, str
    :raise: ``VerifyingDoubleImportError`` if the path is to a top-level module.
    """

    path_segments = path.split(".")
    module_path = ".".join(path_segments[:-1])

    if module_path == "":
        raise VerifyingDoubleImportError("Invalid import path: {}.".format(path))

    class_name = path_segments[-1]

    return module_path, class_name


def get_target(path):
    """Get an object by path

    :param str path: The full path to the objectthat will be targeted.
    :return: The class that will be doubled.
    :rtype: type
    :raise: ``VerifyingDoubleImportError`` if the target object doesn't exist or isn't.
    """

    module_path, class_name = get_path_components(path)
    module = get_module(module_path, path)
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise VerifyingDoubleImportError("No object at path: {}.".format(path))
