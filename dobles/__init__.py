__version__ = "1.5.3"

from dobles.class_double import ClassDouble  # noqa
from dobles.instance_double import InstanceDouble  # noqa
from dobles.lifecycle import (clear, no_builtin_verification, teardown,  # noqa
                              verify)
from dobles.object_double import ObjectDouble  # noqa
from dobles.targets.allowance_target import allow, allow_constructor  # noqa
from dobles.targets.expectation_target import (expect,  # noqa
                                               expect_constructor)
from dobles.targets.patch_target import patch, patch_class  # noqa
