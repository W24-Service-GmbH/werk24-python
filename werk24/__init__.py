"""The werk24 client library.

Importing this package costs what its models cost, and nothing more
---------------------------------------------------------------------

``Werk24Client`` is resolved lazily (PEP 562). It used to be imported here
eagerly, which meant that ``from werk24 import W24AskUnion`` -- or any other
model -- also built the websocket client and everything under it, aiohttp
included.

That is not a hypothetical cost. Five repositories install this package from
main, and three of them never construct a client at all: crew-api's
``handler_read``, ``handler_initialize`` and ``handler_read_with_callback``
import werk24 only to validate a payload, and they are Lambdas, so they pay
the import on every cold start in front of a customer request. Measured on
python 3.13 with the pinned requirements, ``import werk24`` was 784ms, of
which ``werk24.techread`` was 183ms (aiohttp alone 118ms).

Nothing inside this package imports ``werk24.techread`` at module scope --
``werk24.utils.assets`` already defers it inside a function -- so the client
is only built when someone actually asks for it. ``from werk24 import
Werk24Client``, ``werk24.Werk24Client`` and ``from werk24 import *`` all
still work and all still return the same class; the first of them is simply
where the 183ms is spent now.

The models themselves are NOT lazy and should not be made so. They are
pydantic classes built at import, a consumer that imports one generally needs
the discriminated unions that reference the rest, and the v1 compatibility
aliases in ``werk24.models`` rewrite ``sys.modules`` as they load -- deferring
that would make the module graph depend on access order.
"""

from types import ModuleType as _ModuleType
from typing import TYPE_CHECKING

from werk24._version import __version__ as __version__  # noqa: F401
from werk24.models import *  # noqa: F403
from werk24.utils import *  # noqa: F401, F403

if TYPE_CHECKING:  # pragma: no cover - type checkers and IDEs only
    from werk24.techread import Werk24Client as Werk24Client

#: Names bound above that are machinery rather than public API.
_NOT_EXPORTED = {"TYPE_CHECKING"}

#: What ``from werk24 import *`` gives you.
#:
#: Spelled out because a lazy attribute has to be listed to survive a star
#: import: without ``__all__``, ``import *`` copies what is already in
#: ``globals()``, and ``Werk24Client`` is deliberately not there yet. With
#: ``__all__`` the import machinery calls ``getattr`` for each name, which
#: goes through ``__getattr__`` below.
#:
#: Module objects are filtered out for the reason ``werk24.models`` gives in
#: its own ``__all__``: importing a submodule binds it as an attribute of its
#: parent package, so ``models`` and ``utils`` are in ``globals()`` here and
#: would otherwise be re-exported and shadow the real packages.
__all__ = sorted(
    {
        _name
        for _name, _value in list(globals().items())
        if not _name.startswith("_")
        and _name not in _NOT_EXPORTED
        and not isinstance(_value, _ModuleType)
    }
    | {"Werk24Client"}
)

#: Attributes resolved on first access, mapped to the module they live in.
_LAZY_ATTRIBUTES = {"Werk24Client": "werk24.techread"}

#: Submodules that used to be bound here as a side effect of importing them.
#:
#: ``werk24.techread`` was an attribute of this package on any import, because
#: this file imported it. It is not imported any more, so ``import werk24``
#: followed by ``werk24.techread.something`` would raise ``AttributeError``
#: -- a regression that has nothing to do with the name that moved. Resolving
#: it here keeps that spelling working and still defers the cost to first use.
_LAZY_SUBMODULES = {"techread"}


def __getattr__(name: str):
    """Resolve a lazily-exported attribute on first access.

    Args:
        name (str): The attribute asked for on the ``werk24`` package.

    Returns:
        Any: The attribute or submodule, imported from its own module.

    Raises:
        AttributeError: If the name is not one this package exports. It has
            to be ``AttributeError`` rather than ``ImportError`` so that
            ``hasattr``, ``copy`` and ``pickle`` -- all of which probe modules
            for dunder names they do not have -- keep working.
    """
    from importlib import import_module

    if name in _LAZY_SUBMODULES:
        # import_module binds the submodule on this package itself, so the
        # next lookup does not reach __getattr__ at all.
        return import_module(f"{__name__}.{name}")

    module_name = _LAZY_ATTRIBUTES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    value = getattr(import_module(module_name), name)
    # Cache it on the package so later lookups skip __getattr__ entirely.
    globals()[name] = value
    return value


def __dir__() -> list:
    """Keep the lazy names visible to ``dir()`` and to tab completion.

    ``_LAZY_SUBMODULES`` has to be in here as well as ``__all__``, and the
    two lists are not the same list. On main, ``werk24/__init__.py``
    imported ``werk24.techread``, so ``techread`` was bound on this package
    and ``dir(werk24)`` listed it; deferring the import took it out of
    ``globals()``, and without this it would reappear in ``dir()`` only
    after someone had already touched the attribute -- which is precisely
    when they no longer need completion to find it.

    It is deliberately NOT added to ``__all__`` instead. ``__all__`` drives
    ``from werk24 import *``, which would then have to import the submodule
    to bind the name, undoing the change for every star importer, and would
    put a module object back into the star surface that this file filters
    out on purpose.
    """
    return sorted(set(globals()) | set(__all__) | _LAZY_SUBMODULES)
