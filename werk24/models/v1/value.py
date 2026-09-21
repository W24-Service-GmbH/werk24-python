"""Physical quantities, and the pint registry behind them.

The registry is built on first use, not on import
-------------------------------------------------

``UnitRegistry()`` parses pint's whole default unit definition file, and it
costs **182ms** on the pinned requirements -- measured, not estimated. Until
this module deferred it, that was paid by ``import werk24``, because
``werk24.models.v2.asks`` needs ``W24Ask`` for the discriminated ``AskUnion``,
``werk24.models.v1.ask`` pulls ``material``, and ``material`` reaches this
module through ``property.glass_homogeneity``. So every consumer of the
package paid to parse a unit database whether or not it ever handled a
quantity -- ``import werk24`` was 758ms, of which this was very nearly a
quarter.

Five repositories install this package from main, and the crew-api handlers
are Lambdas: they pay that import on every cold start, in front of a
customer's first byte, purely to validate a payload (crew-api#144).

Nothing is lost by deferring it. The registry is reached from exactly two
kinds of place, and neither runs at import any more:

* the ``BeforeValidator`` below, which runs when a quantity is actually
  parsed from a string;
* the ``Field(examples=...)`` in ``property/bubbles_and_inclusions``,
  ``property/stress_birefringence`` and ``property/glass_homogeneity``, which
  used to build a ``W24PhysicalQuantity`` at import to show one example value.
  Those carry the serialized form directly now, which is what the JSON schema
  always contained -- ``tests/test_lazy_unit_registry.py`` pins both halves:
  the schemas are unchanged, and no registry exists after ``import werk24``.

``pint`` itself is still imported here, because ``PintQuantity`` is the
annotated type and pydantic needs the real class when it builds the core
schema. That is 136ms more, and deferring it is a separate and much riskier
change; this one is confined to the object the module constructs.

``ureg`` remains readable as a module attribute (PEP 562), so
``from werk24.models.v1.value import ureg`` still works and still returns the
one shared registry -- it just builds it at that moment rather than at import.
"""

from decimal import Decimal
from typing import Annotated, Optional

from pint import Quantity as PintQuantity
from pint import UnitRegistry
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
)

from .tolerance import W24Tolerance

#: The process-wide registry, once something has asked for one.
#:
#: Module-level rather than an ``lru_cache`` so that ``ureg`` below and every
#: caller of :func:`get_unit_registry` share one registry. Two pint registries
#: in a process do not interoperate: a ``Quantity`` from one raises
#: ``ValueError`` when combined with a ``Quantity`` from the other, so the
#: identity here is a correctness property, not a saving.
_unit_registry: Optional[UnitRegistry] = None


def get_unit_registry() -> UnitRegistry:
    """The shared pint registry, built on first call.

    Returns:
        UnitRegistry: The one registry this process uses for every quantity.
    """
    global _unit_registry
    if _unit_registry is None:
        _unit_registry = UnitRegistry()
    return _unit_registry


def _parse_quantity(value: object) -> object:
    """Coerce *value* to a pint ``Quantity``, leaving one that already is.

    Named rather than a lambda so the registry lookup is legible and so a
    traceback from a bad unit string names this function instead of
    ``<lambda>``.

    Args:
        value (object): Whatever the caller supplied for a quantity field.

    Returns:
        object: *value* unchanged if it is already a ``Quantity``, else the
            result of parsing ``str(value)`` through the shared registry.
    """
    if isinstance(value, PintQuantity):
        return value
    return get_unit_registry()(str(value))


def __getattr__(name: str):
    """Resolve ``ureg`` on first access, so importing this module is cheap.

    Args:
        name (str): The attribute asked for on this module.

    Returns:
        Any: The shared registry, for ``ureg``.

    Raises:
        AttributeError: For any other name. It has to be ``AttributeError``
            rather than ``ImportError`` so that ``hasattr`` and the dunder
            probes ``copy`` and ``pickle`` perform keep working.
    """
    if name == "ureg":
        registry = get_unit_registry()
        # Cache it in the module namespace so later lookups skip __getattr__.
        globals()["ureg"] = registry
        return registry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list:
    """Keep ``ureg`` visible to ``dir()`` before anything has touched it."""
    return sorted(set(globals()) | {"ureg"})


Quantity = Annotated[
    PintQuantity,
    BeforeValidator(_parse_quantity),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
    WithJsonSchema({"type": "string"}, mode="validation"),
]


class W24PhysicalQuantity(BaseModel):
    """Physical Quantity.

    Physical Quantity with a value, unit and tolerance.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    blurb: str = Field(
        title="blurb",
        description="Blurb of the Physical Property for human consumption.",
    )
    value: Quantity = Field(
        title="value", description="Physical quantity in the string format of Pint."
    )
    tolerance: Optional[W24Tolerance] = None


class W24Value(BaseModel):
    blurb: str
    value: Decimal
    tolerance: Optional[W24Tolerance] = None
