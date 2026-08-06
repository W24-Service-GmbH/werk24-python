import types as _types

from .asks import *  # noqa: F403
from .enums import *  # noqa: F403
from .internal import *  # noqa: F403
from .models import *  # noqa: F403
from .responses import *  # noqa: F403
from .status import *  # noqa: F403

# Importing the submodules above binds their names (``asks``, ``enums``,
# ``internal``, ``models``, ``responses``, ``status``) into this package
# namespace as a side effect. Without an explicit ``__all__`` a downstream
# ``from werk24.models.v2 import *`` would re-export those submodule names and,
# in particular, the ``models`` name would overwrite the ``werk24.models``
# package attribute. Restrict star-exports to the actual public symbols and
# exclude any module objects.
__all__ = [
    _name
    for _name, _value in list(globals().items())
    if not _name.startswith("_") and not isinstance(_value, _types.ModuleType)
]
