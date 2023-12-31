from dobles.exceptions import UnallowedMethodCallError
from dobles.instance_double import InstanceDouble
from dobles.target import Target
from dobles.verification import verify_arguments


def patch_class(input_class):
    """Create a new class based on the input_class.

    :param class input_class:  The class to patch.
    :rtype class:
    """

    class Instantiator(object):
        @classmethod
        def _dobles__new__(self, *args, **kwargs):
            pass

    new_class = type(input_class.__name__, (input_class, Instantiator), {})

    return new_class


class ClassDouble(InstanceDouble):
    """
    A pure double representing the target class.

    ::

        User = ClassDouble('myapp.User')

    :param str path: The absolute module path to the class.
    """

    is_class = True

    def __init__(self, path):
        super(ClassDouble, self).__init__(path)
        self._dobles_target = patch_class(self._dobles_target)
        self._target = Target(self._dobles_target)

    def __call__(self, *args, **kwargs):
        """Verify arguments and proxy to _dobles__new__

        :rtype obj:
        :raises VerifyingDoubleArgumentError: If args/kwargs don't match the expected arguments of
            __init__ of the underlying class.
        """
        verify_arguments(self._target, "_dobles__new__", args, kwargs)
        return self._dobles__new__(*args, **kwargs)

    def _dobles__new__(self, *args, **kwargs):
        """Raises an UnallowedMethodCallError

        NOTE: This method is here only to raise if it has not been stubbed
        """
        raise UnallowedMethodCallError(
            "Cannot call __new__ on a ClassDouble without stubbing it"
        )
