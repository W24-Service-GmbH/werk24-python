""" Material Models
"""
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel

from .feature import W24FeatureModel


class W24MaterialCategory1(str, Enum):
    BIOLOGICAL = "BIOLOGICAL"
    CERAMIC = "CERAMIC"
    COMPOSITE = "COMPOSITE"
    GLASS = "GLASS"
    METAL = "METAL"
    POLYMER = "POLYMER"


class W24MaterialCategory2(str, Enum):
    # BIOLOGICAL
    WOOD = "WOOD"

    # CERAMIC
    CARBON = "CARBON"
    ENGINEERING_CERAMIC = "ENGINEERING_CERAMIC"
    NATURAL_CERAMIC = "NATURAL_CERAMIC"

    # COMPOSITE
    CERAMIC_MATRIX_COMPOSITE = "CERAMIC_MATRIX_COMPOSITE"
    METAL_MATRIX_COMPOSITE = "METAL_MATRIX_COMPOSITE"
    POLYMER_MATRIX_COMPOSITE = "POLYMER_MATRIX_COMPOSITE"

    # GLASS
    GLASS_CERAMIC = "GLASS_CERAMIC"
    LEAD_GLASS = "LEAD_GLASS"
    SILICATE_GLASS = "SILICATE_GLASS"

    # METAL
    ALUMINUM = "ALUMINUM"
    BERYLLIUM = "BERYLLIUM"
    CADMIUM = "CADMIUM"
    CHROMIUM = "CHROMIUM"
    CLAD = "CLAD"
    COBALT = "COBALT"
    COPPER = "COPPER"
    HAFNIUM = "HAFNIUM"
    IRON = "IRON"
    LEAD = "LEAD"
    LITHIUM = "LITHIUM"
    MAGNESIUM = "MAGNESIUM"
    MANGANESE = "MANGANESE"
    MOLYBDENUM = "MOLYBDENUM"
    NEODYMIUM = "NEODYMIUM"
    NICKEL = "NICKEL"
    NIOBIUM = "NIOBIUM"
    NOBLE_METAL = "NOBLE_METAL"
    RHENIUM = "RHENIUM"
    SAMARIUM = "SAMARIUM"
    STEEL = "STEEL"
    TANTALUM = "TANTALUM"
    TIN = "TIN"
    TITANIUM = "TITAIUM"
    TUNGSTEN = "TUNGSTEN"
    VANADIUM = "VANADIUM"
    ZIRCONIUM = "ZIRCONIUM"
    ZINC = "ZINC"

    # POLYMER
    ELASTOMER = "ELASTOMER"
    THERMOPLASTIC = "THERMOPLASTIC"
    THERMOSETTING = "THERMOSETTING"


class W24MaterialCategory3(str, Enum):

    # METAL / STEEL
    ALLOY_STEEL = "ALLOY_STEEL"
    CARBON_STEEL = "CARBON_STEEL"
    LOW_ALLOY_STEEL = "LOW_ALLOY_STEEL"
    MARAGING_STEEL = "MARAGING_STEEL"
    STAINLESS_STEEL = "STAINLESS_STEEL"
    TOOL_AND_MACHINING_STEEL = "TOOL_AND_MACHINING_STEEL"

    # METAL / ALUMINIUM
    ALUMINIUM_MASTER_ALLOY = "ALUMINIUM_MASTER_ALLOY"
    CAST_ALUMINIUM = "CAST_ALUMINIUM"
    WROUGHT_ALUMINIUM = "WROUGHT_ALUMINIUM"
    CLAD_BIMETAL = "CLAD/BIMETAL"

    # METAL / COBALT
    COBALT_CHROMIUM = "COBALT_CHROMIUM"
    COBALT_CHROMIUM_MOLYBDENUM = "COBALT_CHROMIUM_MOLYBDENUM"
    COBALT_CHROMIUM_NICKEL_TUNGSTEN = "COBALT_CHROMIUM_NICKEL_TUNGSTEN"
    COBALT_CHROMIUM_TUNGSTEN = "COBALT_CHROMIUM_TUNGSTEN"
    COBALT_NICKEL_CHROMIUM_MOLYBDENUM = "COBALT_NICKEL_CHROMIUM_MOLYBDENUM"
    COBALT_SUPERALLOY = "COBALT_SUPERALLOY"
    UNCLASSIFIED_COBALT_ALLOY = "UNCLASSIFIED_COBALT_ALLOY"

    # METAL / COPPER
    CAST_COPPER = "CAST_COPPER"
    WELDING = "WELDING"
    WROUGHT_COPPER = "WROUGHT_COPPER"

    # METAL / IRON
    ALLOY_IRON = "ALLOY_IRON"
    CAST_IRON = "CAST_IRON"
    FERROMOLYBDENUM = "FERROMOLYBDENUM"
    FERROSILICON = "FERROSILICON"
    FERROVANADIUM = "FERROVANADIUM"
    IRON_ALLOY = "IRON_ALLOY"
    MALLEABLE_CAST_IRON = "MALLEABLE_CAST_IRON"

    # METAL / MAGNESIUM  #to check(grades are confusing)
    ALUMINIUM_GRADE = "ALUMINIUM_GRADE"
    CAST_ALUMINIUM_MANGANESE_GRADE = "CAST_ALUMINIUM_MANGANESE_GRADE"
    CAST_RARE_EARTH_GRADE = "CAST_RARE_EARTH_GRADE"
    CAST_WROUGHT_ALUMINIUM_ZINC_GRADE = "CAST/WROUGHT_ALUMINIUM_ZINC_GRADE"
    CAST_WROUGHT_UNCLASSIFIED_GRADE = "CAST/WROUGHT_UNCLASSIFIED_GRADE"
    PURE_MAGNESIUM = "PURE_MAGNESIUM"
    RARE_EARTH_GRADE = "RARE_EARTH_GRADE"
    WROUGHT_ZINC_GRADE = "WROUGHT_ZINC_GRADE"
    YTTRIUM_GRADE = "YTTRIUM_GRADE"
    ZINC_GRADE = "ZINC_GRADE"
    MANGANESE = "MANGANESE"

    # METAL / NICKEL
    NICKEL_CHROMIUM_ALLOY = "NICKEL_CHROMIUM_ALLOY"
    NICKEL_CHROMIUM_COBALT_ALLOY = "NICKEL_CHROMIUM_COBALT_ALLOY"
    NICKEL_CHROMIUM_IRON_ALLOY = "NICKEL_CHROMIUM_IRON_ALLOY"
    NICKEL_CHROMIUM_MOLYBDENUM_ALLOY = "NICKEL_CHROMIUM_MOLYBDENUM_ALLOY"
    NICKEL_COBALT_ALLOY = "NICKEL_COBALT_ALLOY"
    NICKEL_COPPER_ALLOY = "NICKEL_COPPER_ALLOY"
    NICKEL_IRON_ALLOY = "NICKEL_IRON_ALLOY"
    NICKEL_MOLYBDENUM_ALLOY = "NICKEL_MOLYBDENUM_ALLOY"
    NICKEL_WELDING_FILLER = "NICKEL_WELDING_FILLER"
    OTHER_NICKEL_ALLOY = "OTHER_NICKEL_ALLOY"
    PURE_LOW_NICKEL_ALLOY = "PURE/LOW_NICKEL_ALLOY"

    # METAL / NOBLE
    GOLD = "GOLD"
    IRIDIUM = "IRIDIUM"
    PALLADIUM = "PALLADIUM"
    PLATINUM = "PLATINUM"
    RHODIUM = "RHODIUM"
    SILVER = "SILVER"

    # METAL / REFRACTORY
    HAFNIUM = "HAFNIUM"
    MOLYBDENUM = "MOLYBDENUM"
    NIOBIUM = "NIOBIUM"
    RHENIUM = "RHENIUM"
    TANTALUM = "TANTALUM"
    TUNGSTEN = "TUNGSTEN"
    VANADIUM = "VANADIUM"
    ZIRCONIUM = "ZIRCONIUM"

    # METAL / TITANIUM
    ALPHA_ALLOY = "ALPHA_ALLOY"
    ALPHA_BETA_ALLOY = "ALPHA_BETA_ALLOY"
    BETA_ALLOY = "BETA_ALLOY"
    LOW_ALLOY_TITANIUM = "LOW_ALLOY_TITANIUM"
    NEAR_ALPHA_ALLOY = "NEAR_ALPHA_ALLOY"
    PURE_TITANIUM = "PURE_TITANIUM"

    # POLYMER / ELASTOMER
    BUTADIENE_RUBBER = "BUTADIENE_RUBBER"
    CHLOROPRENE_RUBBER = "CHLOROPRENE_RUBBER"
    ELASTOMETRIC_ALLOY = "ELASTOMETRIC_ALLOY"
    ETHYLENE_PROPYLENE_DIENE_RUBBER = "ETHYLENE_PROPYLENE_DIENE_RUBBER"
    ETHYLENE_PROPYLENE_RUBBER = "ETHYLENE_PROPYLENE_RUBBER"
    FLUOROSILICICONE_RUBBER = "FLUOROSILICONE_RUBBER"
    NATURAL_RUBBER = "NATURAL_RUBBER"
    NITRILE_RUBBER = "NITRILE_RUBBER"
    SYTRENE_BUTADIENE_RUBBER = "SYTRENE_BUTADIENE_RUBBER"
    SYTRENE_BUTADIENE_STYRENE = "STYRENE_BUTADIENE_STYRENE"
    THERMOPLASTIC_COPOLYESTER = "THERMOPLASTIC_COPOLYESTER"
    THERMOPLASTIC_POLYAMIDE = "THERMOPLASTIC_POLYAMIDE"
    THERMOPLASTIC_POLYESTER_ELASTOMER = "THERMOPLASTIC_POLYESTER_ELASTOMER"
    THERMOPLASTIC_POLYOLEFIN = "THERMOPLASTIC_POLYOLEFIN"
    THERMOPLASTIC_POLYURETHANE = "THERMOPLASTIC_POLYURETHANE"
    THERMOPLASTIC_STYRENIC_BLOCK_COPOLYMER = "THERMOPLASTIC_STYRENIC_BLOCK_COPOLYMER"

    # POLYMER / THERMOPLASTIC
    POLYACRYLONITRILE = "POLYACRYLONITRILE"
    POLYMETHYL_METHACRYLATE = "POLYMETHYL_METHACRYLATE"
    FLUOROPOLYMER = "FLUOROPOLYMER"
    ETHYLENE_TETRAFLUOROETHYLENE_COPOLYMER = "ETHYLENE_TETRAFLUOROETHYLENE_COPOLYMER"
    FLUORINATED_ETHYLENE_PROPYLENE = "FLUORINATED_ETHYLENE_PROPYLENE"
    POLYTETRAFLUOROETHYLENE = "POLYTETRAFLUOROETHYLENE"
    POLYVINYLIDENEFLUORIDE = "POLYVINYLIDENEFLUORIDE"
    LIQUID_CRYSTAL_POLYMERS = "LIQUID_CRYSTAL_POLYMERS"
    POLYAMIDE = "POLYAMIDE"
    ARAMIDE = "ARAMIDE"
    COPOLYAMIDE_6_66 = "COPOLYAMIDE_6/66"
    OTHER_POLYAMIDE = "OTHER_POLYAMIDE"
    POLYAMIDE_1010 = "POLYAMIDE_1010"
    POLYAMIDE_1012 = "POLYAMIDE_1012"
    POLYAMIDE_11 = "POLYAMIDE_11"
    POLYAMIDE_12 = "POLYAMIDE_12"
    POLYAMIDE_410 = "POLYAMIDE_410"
    POLYAMIDE_46 = "POLYAMIDE_46"
    POLYAMIDE_6 = "POLYAMIDE_6"
    POLYAMIDE_4T = "POLYAMIDE_4T"
    POLYAMIDE_6_66 = "POLYAMIDE_6/66"
    POLYAMIDE_610 = "POLYAMIDE_610"
    POLYAMIDE_612 = "POLYAMIDE_612"
    POLYAMIDE_66 = "POLYAMIDE_66"
    POLYPHTHALAMIDE = "POLYPHTHALAMIDE"
    COPOLYAMIDE_6_66 = "COPOLYAMIDE_6/66"
    COPOLYAMIDE_66_6I = "COPOLYAMIDE_66/6I"
    COPOLYAMIDE_6I_6T = "COPOLYAMIDE_6I/6T"
    COPOLYAMIDE_6T_66 = "COPOLYAMIDE_6T/66"
    COPOLYAMIDE_6T_6I_66 = "COPOLYAMIDE_6T/6I/66"
    COPOLYAMIDE_PA6I_6T = "COPOLYAMIDE_PA6I/6T"
    POLYAMIDE_4T = "POLYAMIDE_4T"
    POLYAMIDE_6T = "POLYAMIDE_6T"
    POLYAMIDE_MXD6 = "POLYAMIDE_MXD6"
    POLYAMIDE_PA6_6T = "POLYAMIDE_PA6/6T"
    POLYARYLETHERKETONE = "POLYARYLETHERKETONE"
    POLYETHER_KETONE = "POLYETHER_KETONE"
    POLYETHERETHER_KETONE = "POLYETHERETHER_KETONE"
    POLYETHERKETONEKETONE = "POLYETHERKETONEKETONE"
    POLYCARBONATE = "POLYCARBONATE"
    POLYESTER = "POLYESTER"
    POLYBUTYLENE_TEREPHTHALATE = "POLYBUTYLENE_TEREPHTHALATE"
    POLYETHYLENE_TEREPHTHALATE = "POLYETHYLENE_TEREPHTHALATE"
    POLYETHYLENE_TEREPHTHALATE_GLYCOL = "POLYETHYLENE_TEREPHTHALATE_GLYCOL"
    POLYGLYCOLICIDE = "POLYGLYCOLICIDE"
    POLYTRIMETHYLENE_TEREPHTHALATE = "POLYTRIMETHYLENE_TEREPHTHALATE"
    POLYETHYLENE = "POLYETHYLENE"
    POLYIMIDE = "POLYIMIDE"
    POLYAMIDIMIDE = "POLYAMIDIMIDE"
    POLYBENZIMIDAZOLE = "POLYBENZIMIDAZOLE"
    POLYETHERIMIDE = "POLYETHERIMIDE"
    POLYKETONE = "POLYKETONE"
    POLYLACTIC_ACID = "POLYLACTIC_ACID"
    POLYMER_BLEND = "POLYMER_BLEND"
    ACRYLONITRILE_BUTADIENE_STYRENE = "ACRYLONITRILE_BUTADIENE_STYRENE"
    POLYOLEFIN = "POLYOLEFIN"
    POLYBUTENE = "POLYBUTENE"
    POLYETHYLENE = "POLYETHYLENE"
    POLYMETHYLPENTENE = "POLYMETHYLPENTENE"
    POLYPROPYLENE = "POLYPROPYLENE"
    POLYOXYMETHYLENE = "POLYOXYMETHYLENE"
    POLYPHENYL = "POLYPHENYL"
    POLYPHENYL_ETHER = "POLYPHENYL_ETHER"
    POLYPHENYLENE_OXIDE = "POLYPHENYLENE_OXIDE"
    POLYPHENYLENE_SULFIDE = "POLYPHENYLENE_SULFIDE"
    POLYSACCHARIDE = "POLYSACCHARIDE"
    POLYSULPHONES = "POLYSULPHONES"
    POLYETHER_SULFONE = "POLYETHER_SULFONE"
    POLYPHENYLSULPHONE = "POLYPHENYLSULPHONE"
    POLYSULPHONE = "POLYSULPHONE"
    POLYSULPHONE_GENERAL = "POLYSULPHONE_GENERAL"
    STYRENE = "STYRENE"
    ACRYLONITRILE_BUTADIENE_STYRENE = "ACRYLONITRILE_BUTADIENE_STYRENE"
    ACRYLONITRILE_STYRENE_ACRYLATE = "ACRYLONITRILE_STYRENE_ACRYLATE"
    HIGH_IMPACT_POLYSTYRENE = "HIGH_IMPACT_POLYSTYRENE"
    METHACRYLATE_BUTADIENE_STYRENE = "METHACRYLATE_BUTADIENE_STYRENE"
    POLYSTYRENE = "POLYSTYRENE"
    STYRENE_ACRYLONITRILE = "STYRENE_ACRYLONITRILE"
    VINYL = "VINYL"
    ETHYLENE_VINYL_ACETATE = "ETHYLENE_VINYL_ACETATE"
    POLYVINYL_CHLORIDE = "POLYVINYL_CHLORIDE"

    # POLYMER  / THERMOSETTING
    AMINO_RESIN = "AMINO_RESIN"
    BISMALEIMIDE = "BISMALEIMIDE"
    MELAMINE_FORMALDEHYDE = "MELAMINE_FORMALDEHYDE"
    EPOXY_RESIN = "EPOXY_RESIN"
    PHENOL_FORMALDEHYDE_RESIN = "PHENOL_FORMALDEHYDE_RESIN"
    PHTHALONITRILE = "PHTHALONITRILE"
    POLYESTER_RESIN = "POLYESTER_RESIN"
    VINYL_ESTER_RESIN = "VINYL_ESTER_RESIN"


class W24MaterialFamily(str, Enum):
    """ Material Family: First level
    Following the material categorization of Michael F. Ashby
    """
    METAL = "METAL"
    NONMETAL = "NONMETAL"
    HYBRID = "HYBRID"


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

    AUSTENTIC = "AUSTENTIC"
    """ Steel name conventions,
    e.g,. V2A
    """

    BLOB = "BLOB"
    """ Blob material names,
    e.g., steel
    """

    EN573 = "EN573"
    """ Material name of materail number following
    the EN573-3 standard for aluminums
    """

    EN10027 = "EN10027"
    """ Material name or material number following
    the EN 10027-1 and EN 10027-2 standard
    """

    EN10210 = "EN10210"
    """ Material make following the EN10210 standard
    for steel tubes
    """

    EN10263 = "EN10263"
    """ Material number following the EN 10264
    standard
    """

    ISO898 = "ISO898"
    """ Material name following the ISO 909
    for metric fasterns.
    """

    ISO1043 = "ISO1043"
    """ Material number following the EN 1043
    standard
    """

    ISO1874 = "ISO1874"
    """ Material number following the EN 1874-1
    standard
    """

    DIN17100_1987_12 = "DIN17100:1987-12"
    """ DIN17100:1987-12
    """


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
