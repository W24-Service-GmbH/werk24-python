

# from decimal import Decimal
# from enum import Enum
# from typing import Optional

# from pydantic import BaseModel


# class W24Dimension(str, Enum):
#     """Dimensions for the Physical Quantities.

#     NOTE: This list might grow as we add additional
#     properties to our database.
#     """
#     # start with the SI base dimensions
#     LENGTH = "LENGTH"  # [m]
#     MASS = "MASS"  # [kg]
#     TIME = "TIME"  # [s]
#     ELECTRIC_CURRENT = "ELECTRIC_CURRENT"  # [A]
#     THERMODYNAMIC_TEMPERATURE = "THERMODYNAMIC_TEMPERATURE"  # [K]
#     AMOUNT_OF_SUBSTANCE = "AMOUNT_OF_SUBSTANCE"  # [mol]
#     LUMINOUS_INTENSITY = "LUMINOUS_INTENSITY"  # [cd]

#     # derived SI dimensions
#     AREA = "AREA"  # [m2]
#     VOLUME = "VOLUME"  # [m2]
#     VELOCITY = "VELOCITY"  # [m/s]
#     ACCELERATION = "ACCELERATION"  # [m/s2]
#     FORCE = "FORCE"  # [N]
#     PRESSURE = "PRESSURE"  # [Pa]
#     ENERGY = "ENERGY"  # [J]
#     POWER = "POWER"  # [W]
#     ELECTRIC_CHARGE = "ELECTRIC_CHARGE"  # [C]
#     ELECTRIC_POTENTIAL = "ELECTRIC_POTENTIAL"  # [V]
#     ELECTRIC_RESISTANCE = "ELECTRIC_RESISTANCE"  # [OHM]
#     MAGNETIC_FLUX = "MAGNETIC_FLUX"  # [Wb]
#     MAGNETIC_FIELD = "MAGNETIC_FIELD"  # [T]

#     # commonly used derived dimensions
#     LINEAR_DENSITY = "LINEAR_DENSITY"  # [kg/m]
#     AREA_DENSITY = "AREA_DENSITY"  # [kg/m2]
#     MASS_DENSITY = "MASS_DENSITY"  # [kg/m3]


# class W24UnitPrefix(Decimal, Enum):
#     """List of the Unit Prefixes in the SI system.

#     NOTE: the Chinese and Indian systems are based
#     on multiples of 10'000. There are other numbering
#     systems that work on multiples of 12 or 6.
#     """
#     YOTTA = Decimal("10")**24
#     ZETTA = Decimal("10")**21
#     EXA = Decimal("10")**18
#     PETA = Decimal("10")**15
#     TERA = Decimal("10")**12
#     GIGA = Decimal("10")**9
#     MEGA = Decimal("10")**6
#     KILO = Decimal("10")**3
#     HECTO = Decimal("10")**2
#     DECA = Decimal("10")**1
#     DECI = Decimal("10")**-1
#     CENTI = Decimal("10")**-2
#     MILLI = Decimal("10")**-3
#     MICRO = Decimal("10")**-6
#     NANO = Decimal("10")**-9
#     PICO = Decimal("10")**-12
#     FEMTO = Decimal("10")**-15
#     ATTO = Decimal("10")**-18
#     ZEPTO = Decimal("10")**-21
#     YOCTO = Decimal("10")**-24


# class W24Unit(BaseModel):
#     """Physical Unit.

#     Attributes:
#         dimension (W24Dimension): Dimension that is
#             measured by the unit.
#         name (str): Name of the unit.
#         symbol (str): Symbol of the unit. E.g. `l` for liter.
#         unit_prefix (Optional[W24UnitPrefix]): Optional Unit
#             prefix. For example: milli or Mega.
#         unit_power (int): Power of the unit. Eg. 3 for volumes.
#         si_multiple (Decimal): Factor by which the value
#             needs to be multiplied to obtain the SI value of
#             the dimension.

#     """
#     dimension: W24Dimension
#     name: str
#     symbol: str
#     unit_prefix: Optional[W24UnitPrefix]
#     unit_power: int = 1
#     si_factor: Decimal


# class W24UnitFactory:
#     """Factory to create the Units.
#     """

#     @classmethod
#     def _make(
#         cls,
#         dimension: W24Dimension,
#         config_options,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix],
#         unit_power: int = 1
#     ) -> W24Unit:

#         # get the configuration.
#         config = config_options.get(name)
#         if config is None:
#             raise ValueError()

#         return W24Unit(
#             dimension=dimension,
#             unit_prefix=unit_prefix,
#             unit_power=unit_power,
#             symbol=config[0],
#             name=name,
#             si_factor=Decimal(config[1])
#         )

#     @classmethod
#     def make_length(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         config = {
#             "meter": ("m", "1"),
#             "inch": ("in",  "0.0254"),
#             "foot": ("ft",  "0.3048"),
#         }
#         return cls._make(W24Dimension.LENGTH, config, name, unit_prefix)

#     @classmethod
#     def make_area(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         config = {
#             "square meter": ("m2",  "1"),
#             "square inch": ("in2",  "0.0254"),
#             "square foot": ("ft2",  "0.3048"),
#         }
#         return cls._make(W24Dimension.AREA, config, name, unit_prefix, 2)

#     @classmethod
#     def make_volume(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         config = {
#             "cubic meter": ("m3", "1"),
#             "cubic inch": ("in3", "0.0254"),
#             "cubic foot": ("ft3", "0.3048"),
#             "liter": ("l", "0.001"),
#         }
#         return cls._make(W24Dimension.VOLUME, config, name, unit_prefix, 3)

#     @classmethod
#     def make_time(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         # NOTE: a day can sometimes be shorter than 86400 seconds;
#         # but as measurement unit, we'll accept this.
#         config = {
#             "day": ("day", "86400"),
#             "hour": ("h", "3600"),
#             "minute": ("min",  "60"),
#             "second": ("s",  "1"),
#         }
#         return cls._make(W24Dimension.TIME, config, name, unit_prefix, 1)

#     @classmethod
#     def make_mass(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         config = {
#             "tonne": ("t", "1000"),
#             "gram": ("g", "0.001"),
#             "pound": ("lb", "0.453592"),
#             "ounce": ("oz",  "0.0283495"),
#             "stone": ("oz",  "6.35029"),
#             "slug": ("slug", "14.5939"),
#             "carat": ("ct", "0.0002"),
#         }
#         return cls._make(W24Dimension.MASS, config, name, unit_prefix, 1)

#     @classmethod
#     def make_linear_density(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         config = {
#             "tonne per meter": ("t/m", "1000"),
#             "gram per meter": ("g/m", "0.001"),
#             "pound per meter": ("lb/m", "0.453592"),
#             "ounce per meter": ("oz/m",  "0.0283495"),
#             "stone per meter": ("oz/m",  "6.35029"),
#             "slug per meter": ("slug/m", "14.5939"),
#             "carat per meter": ("ct/m", "0.0002"),

#             "tonne per inch": ("t/in", "39370.1"),
#             "gram per inch": ("g/in", "0.0393701"),
#             "pound per inch": ("lb/in", "17.858"),
#             "ounce per inch": ("oz/in",  "1.11612"),
#             "stone per inch": ("oz/in",  "250.012"),
#             "slug per inch": ("slug/in", "574.563"),
#             "carat per inch": ("ct/in", "0.00787402"),
#         }
#         return cls._make(W24Dimension.LINEAR_DENSITY, config, name, unit_prefix, 1)

#     @classmethod
#     def make_force(
#         cls,
#         name: str,
#         unit_prefix: Optional[W24UnitPrefix] = None
#     ) -> W24Unit:
#         config = {
#             "dyne": ("dyn", "0.00001"),
#             "newton": ("N", "1"),
#             "kilogram-force": ("kgf", "9.806650")
#         }
#         return cls._make(W24Dimension.FORCE, config, name, unit_prefix, 1)


# class W24PhysicalQuantity(BaseModel):
#     value: Decimal
#     unit: W24Unit

#     def convert_to(self, new_unit: W24Unit):

#         if self.unit.dimension != new_unit.dimension:
#             raise ValueError("Cannot change dimensions in conversion.")

#         # get the value in the base value
#         power = self.unit.unit_power
#         base_value = self.value * (self.unit.unit_prefix or 1)**power
#         factor = (self.unit.si_factor / new_unit.si_factor)
#         value = base_value * factor**power
#         return W24PhysicalQuantity(value=value, unit=new_unit)

#     def __str__(self) -> str:
#         unit_prefix = {
#             W24UnitPrefix.YOTTA: "Y",
#             W24UnitPrefix.ZETTA: "Z",
#             W24UnitPrefix.EXA: "E",
#             W24UnitPrefix.PETA: "P",
#             W24UnitPrefix.TERA: "T",
#             W24UnitPrefix.GIGA: "G",
#             W24UnitPrefix.MEGA: "M",
#             W24UnitPrefix.KILO: "k",
#             W24UnitPrefix.HECTO: "h",
#             W24UnitPrefix.DECA: "da",
#             None: "",
#             W24UnitPrefix.DECI: "d",
#             W24UnitPrefix.CENTI: "c",
#             W24UnitPrefix.MILLI: "m",
#             W24UnitPrefix.MICRO: "µ",
#             W24UnitPrefix.NANO: "n",
#             W24UnitPrefix.PICO: "p",
#             W24UnitPrefix.FEMTO: "f",
#             W24UnitPrefix.ATTO: "a",
#             W24UnitPrefix.ZEPTO: "z",
#             W24UnitPrefix.YOCTO: "y",
#         }.get(self.unit.unit_prefix)

#         # make sure we have actually found
#         # the value.
#         if unit_prefix is None:
#             raise ValueError("Unknown unit prefix")

#         return f"{self.value} {unit_prefix}{self.unit.symbol}"
