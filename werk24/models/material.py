""" Material Models
"""
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from .feature import W24FeatureModel


class W24MaterialFamily(str, Enum):
    """ Material Family: First level
    Following the material categorization of Michael F. Ashby
    """
    CERAMIC = "CERAMIC"
    COMPOSITE = "COMPOSITE"
    GLASS = "GLASS"
    METAL = "METAL"
    POLYMER = "POLYMER"


class W24MaterialClassMetal(str, Enum):
    """ Material Class: Second level for Metals
    """
    FERROUS = "FERROUS"
    NONFERROUS = "NONFERROUS"


class W24MaterialClassNonmetal(str, Enum):
    """ Material Class: Second level for Nonmetals
    """
    NATURAL = "NATURAL"
    ARTIFICIAL = "ARTIFICIAL"


class W24MaterialClassHybrid(str, Enum):
    """ Material Class: Second level for Hybrids
    """
    COMPOSITE = "COMPOSITE"
    CELLULAR = "CELLULAR"


class W24MaterialTypeMetalFerrous(str, Enum):
    """ Material Type: Third level for Metals/Ferrous
    """
    STEEL = "STEEL"
    CAST_IRON = "CAST_IRON"


class W24MaterialTypeMetalNonferrous(str, Enum):
    """ Material Type: Third level for Metals/Nonferrous
    """
    HEAVY_METAL = "HEAVY_METAL"
    LIGHT_METAL = "LIGHT_METAL"


class W24MaterialGroupMetalFerrousSteel(str, Enum):
    """ Material Group: Fourth level for Metals/Ferrous/Steel
    """
    STRUCTURAL_STEEL = "STRUCTURAL_STEEL"
    STAINLESS_STEEL = "STAINLESS_STEEL"
    TOOL_STEEL = "TOOL_STEEL"


class W24MaterialGroupMetalFerrousCastIron(str, Enum):
    """ Material Group: Fourth level for Metals/Ferrous/CastIron
    """
    CAST_IRON = "CAST_IRON"
    GRAY_IRON = "GRAY_IRON"
    STEEL_CASTING = "STEEL_CASTING"


class W24MaterialGroupMetalNonferrousHeavyMetal(str, Enum):
    """ Material Group: Fourth level for Metals/Nonferrous/HeavyMetal
    """
    ANTIMONY = "ANTIMONY"
    CERIUM = "CERIUM"
    DYSPROSIUM = "DYSPROSIUM"
    ERBIUM = "ERBIUM"
    EUROPIUM = "EUROPIUM"
    GADOLINIUM = "GADOLINIUM"
    GALLIUM = "GALLIUM"
    GERMANIUM = "GERMANIUM"
    HOLMIUM = "HOLMIUM"
    INDIUM = "INDIUM"
    LANTHANUM = "LANTHANUM"
    LUTETIUM = "LUTETIUM"
    NEODYMIUM = "NEODYMIUM"
    NIOBIUM = "NIOBIUM"
    PRASEODYMIUM = "PRASEODYMIUM"
    SAMARIUM = "SAMARIUM"
    TANTALUM = "TANTALUM"
    TERBIUM = "TERBIUM"
    THULIUM = "THULIUM"
    TUNGSTEN = "TUNGSTEN"
    URANIUM = "URANIUM "
    YTTERBIUM = "YTTERBIUM"
    IRIDIUM = "IRIDIUM"
    OSMIUM = "OSMIUM"
    PALLADIUM = "PALLADIUM"
    PLATINUM = "PLATINUM"
    RHODIUM = "RHODIUM"
    RUTHENIUM = "RUTHENIUM"
    GOLD = "GOLD"
    SILVER = "SILVER"
    CHROMIUM = "CHROMIUM"
    COBALT = "COBALT"
    COPPER = "COPPER"
    LEAD = "LEAD"
    MOLYBDENUM = "MOLYBDENUM"
    NICKEL = "NICKEL"
    TIN = "TIN"
    ZINC = "ZINC"
    ARSENIC = "ARSENIC"
    BISMUTH = "BISMUTH"
    CADMIUM = "CADMIUM"
    HAFNIUM = "HAFNIUM"
    MANGANESE = "MANGANESE"
    MERCURY = "MERCURY"
    PROTACTINIUM = "PROTACTINIUM"
    RHENIUM = "RHENIUM"
    SELENIUM = "SELENIUM"
    TELLURIUM = "TELLURIUM"
    THALLIUM = "THALLIUM"
    THORIUM = "THORIUM"
    VANADIUM = "VANADIUM"
    ZIRCONIUM = "ZIRCONIUM"
    ACTINIUM = "ACTINIUM"
    AMERICIUM = "AMERICIUM"
    BERKELIUM = "BERKELIUM"
    CALIFORNIUM = "CALIFORNIUM"
    CURIUM = "CURIUM"
    DUBNIUM = "DUBNIUM"
    EINSTEINIUM = "EINSTEINIUM"
    FERMIUM = "FERMIUM"
    MENDELEVIUM = "MENDELEVIUM"
    NEPTUNIUM = "NEPTUNIUM"
    PLUTONIUM = "PLUTONIUM"
    POLONIUM = "POLONIUM"
    PROMETHIUM = "PROMETHIUM"
    RADIUM = "RADIUM"
    TECHNETIUM = "TECHNETIUM"
    ASTATINE = "ASTATINE"
    BOHRIUM = "BOHRIUM"
    COPERNICIUM = "COPERNICIUM"
    DARMSTADTIUM = "DARMSTADTIUM"
    FLEROVIUM = "FLEROVIUM"
    HASSIUM = "HASSIUM"
    LAWRENCIUM = "LAWRENCIUM"
    LIVERMORIUM = "LIVERMORIUM"
    MEITNERIUM = "MEITNERIUM"
    MOSCOVIUM = "MOSCOVIUM"
    NIHONIUM = "NIHONIUM"
    NOBELIUM = "NOBELIUM"
    ROENTGENIUM = "ROENTGENIUM"
    RUTHERFORDIUM = "RUTHERFORDIUM"
    SEABORGIUM = "SEABORGIUM"
    TENNESSINE = "TENNESSINE"


class W24MaterialGroupMetalNonferrousLightMetal(str, Enum):
    """ Material Group: Fourth level for Metals/Nonferrous/LightMetal
    """
    LITHIUM = "LITHIUM"
    BERYLLIUM = "BERYLLIUM"
    BORON = "BORON"
    SODIUM = "SODIUM"
    MAGNESIUM = "MAGNESIUM"
    ALUMINUM = "ALUMINUM"
    SILICON = "SILICON"
    POTASSIUM = "POTASSIUM"
    CALCIUM = "CALCIUM"
    SCANDIUM = "SCANDIUM"
    TITANIUM = "TITANIUM"
    RUBIDIUM = "RUBIDIUM"
    STRONTIUM = "STRONTIUM"
    YTTRIUM = "YTTRIUM"
    CAESIUM = "CAESIUM"
    BARIUM = "BARIUM"
    FRANCIUM = "FRANCIUM"


W24MaterialClass = Union[
    W24MaterialClassMetal,
    W24MaterialClassNonmetal,
    W24MaterialClassHybrid
]

W24MaterialType = Union[
    W24MaterialTypeMetalFerrous,
    W24MaterialTypeMetalNonferrous
]

W24MaterialGroup = Union[
    W24MaterialGroupMetalFerrousSteel,
    W24MaterialGroupMetalFerrousCastIron,
    W24MaterialGroupMetalNonferrousHeavyMetal,
    W24MaterialGroupMetalNonferrousLightMetal,
]


class W24MaterialStandard(str, Enum):
    """ Enum all the supported
    Material Standards
    """

    # BLURB
    AUSTENITIC = "AUSTENITIC"
    BLOB = "BLOB"
    COMPANY_STANDARD = "COMPANY STANDARD"

    # ASTM
    ASTM_A193 = "ASTM A193"
    ASTM_A307 = "ASTM A307"
    ASTM_A1008 = "ASTM A1008"
    ASTM_F568M = "ASTM F568M"

    # DIN
    DIN1652 = "DIN 1652"
    DIN17100 = "DIN 17100"
    DIN17204 = "DIN 17204"

    # EN
    EN573 = "EN 573"
    EN10027 = "EN 10027"
    EN10083 = "EN 10083"
    EN10132 = "EN 10132"
    EN10210 = "EN 10210"
    EN10219 = "EN 10219"
    EN10263 = "EN 10263"

    # ISO
    ISO898 = "ISO 898"
    ISO1043 = "ISO 1043"

    # JIS
    JIS_G3505 = "JIS G3505"
    JIS_G3507 = "JIS G3507"

    # SAE
    SAE_J403 = "SAE J403"
    SAE_J429 = "SAE J429"
    SAE_J1086 = "SAE J1086"
    SAE_HS1086 = "SAE HS-1086"


class W24MaterialReference(BaseModel):
    """ List of equivalent materials in one of the
    European standards. Either EN10027-1 for steels
    or EN573-3 for aluminums.

    Attributes:
        material_standard: Material standard used for the
            equivalents.
        material_codes: List of equivalent material codes
            in the chosen material_standard
    """
    material_standard: W24MaterialStandard

    material_codes: List[str]


class W24Material(W24FeatureModel):
    """ Parsed Material object that can either be
    associated to the TitleBlock or derived from
    all the available information (including the
    text on the canvas

    Attributes:
        blurb: Material Name for human consumption

        material_family: Material Family (Metal, Nonmetal, Hybrid)
            following the classification system of Michael Ashby.
            Values are only set to the level on which they are defined.
            For example, the material blob "Steel" will translate to
            METAL/FERROUS/STEEL/None

        material_class: Second level material classification

        material_type: Third level material classification

        material_group: Fourth level material classification

        material_standard: Material Standard indicated
            on the technical drawing

        material_code: Name of the material in accordance
            with the material standard

        reference_materials: Optional translation of the
            Material into a list of equivalent materials
    """

    blurb: str

    material_family: Optional[W24MaterialFamily] = None
    material_class: Optional[W24MaterialClass] = None
    material_type: Optional[W24MaterialType] = None
    material_group: Optional[W24MaterialGroup] = None

    material_standard: W24MaterialStandard

    material_code: str

    reference_material: Optional[W24MaterialReference] = None
