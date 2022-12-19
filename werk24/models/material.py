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
    LEATHER = "LEATHER"
    PAPER = "PAPER"
    WAX = "WAX"
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
    BRASS = "BRASS"
    BRONZE = "BRONZE"
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

    # METAL / ALUMINIUM
    ALUMINIUM_ALLOY = "ALUMINIUM_ALLOY"
    CAST_ALUMINIUM = "CAST_ALUMINIUM"
    CLAD_BIMETAL = "CLAD/BIMETAL"
    WROUGHT_ALUMINIUM = "WROUGHT_ALUMINIUM"

    # METAL / BRASS
    ALPHA_BRASS = "ALPHA_BRASS"
    ALPHA_BETA_BRASS = "ALPHA_BETA_BRASS"
    BETA_BRASS = "BETA_BRASS"
    GAMMA_BRASS = "GAMMA_BRASS"
    WHITE_BRASS = "WHITE_BRASS"

    # METAL / BRONZE
    ALUMINIUM_BRONZE = "ALUMINIUM_BRONZE"
    BEARING_BRONZE = "BEARING_BRONZE"
    BISMUTH_BRONZE = "BISMUTH_BRONZE"
    COPPER_NICKEL_BRONZE = "COPPER_NICKEL_BRONZE"
    MANGANESE_BRONZE = "MANGANESE_BRONZE"

    # METAL / COBALT
    COBALT_CHROMIUM = "COBALT_CHROMIUM"
    COBALT_CHROMIUM_MOLYBDENUM = "COBALT_CHROMIUM_MOLYBDENUM"
    COBALT_CHROMIUM_NICKEL_TUNGSTEN = "COBALT_CHROMIUM_NICKEL_TUNGSTEN"
    COBALT_CHROMIUM_TUNGSTEN = "COBALT_CHROMIUM_TUNGSTEN"
    COBALT_NICKEL_CHROMIUM_MOLYBDENUM = "COBALT_NICKEL_CHROMIUM_MOLYBDENUM"
    COBALT_SUPERALLOY = "COBALT_SUPERALLOY"

    # METAL / COPPER
    CAST_COPPER = "CAST_COPPER"
    WELDING_COPPER = "WELDING_COPPER"
    WROUGHT_COPPER = "WROUGHT_COPPER"

    # METAL / IRON
    CAST_IRON = "CAST_IRON"
    FERROMOLYBDENUM = "FERROMOLYBDENUM"
    FERROSILICON = "FERROSILICON"
    FERROVANADIUM = "FERROVANADIUM"
    IRON_ALLOY = "IRON_ALLOY"

    # METAL / MAGNESIUM
    MAGNESIUM_ALUMINIUM_MANGANESE = "MAGNESIUM_ALUMINIUM_MANGANESE"
    MAGNESIUM_ALUMINIUM_SILICON_MANGANESE = "MAGNESIUM_ALUMINIUM_SILICON_MANGANESE"
    MAGNESIUM_ALUMINIUM_STRONTIUM = "MAGNESIUM_ALUMINIUM_STRONTIUM"
    MAGNESIUM_ALUMINIUM_ZINC_MANGANESE = "MAGNESIUM_ALUMINIUM_ZINC_MANGANESE"
    MAGNESIUM_MANGANESE = "MAGNESIUM_MANGANESE"
    MAGNESIUM_PURE = "MAGNESIUM_PURE"
    MAGNESIUM_RARE_EARTH = "MAGNESIUM_RARE_EARTH"
    MAGNESIUM_RARE_EARTH_ZIRCONIUM = "MAGNESIUM_RARE_EARTH_ZIRCONIUM"
    MAGNESIUM_SILVER_RARE_EARTH_ZIRCONIUM = "MAGNESIUM_SILVER_RARE_EARTH_ZIRCONIUM"
    MAGNESIUM_YTTRIUM = "MAGNESIUM_YTTRIUM"
    MAGNESIUM_YTTRIUM_RARE_EARTH_ZIRCONIUM = "MAGNESIUM_YTTRIUM_RARE_EARTH_ZIRCONIUM"
    MAGNESIUM_ZINC = "MAGNESIUM_ZINC"
    MAGNESIUM_ZINC_COPPER_MANGANESE = "MAGNESIUM_ZINC_COPPER_MANGANESE"
    MAGNESIUM_ZINC_ZIRCONIUM = "MAGNESIUM_ZINC_ZIRCONIUM"
    MAGNESIUM_ZIRCONIUM = "MAGNESIUM_ZIRCONIUM"

    # METAL / NICKEL
    NICKEL_CHROMIUM_ALLOY = "NICKEL_CHROMIUM_ALLOY"
    NICKEL_CHROMIUM_COBALT_ALLOY = "NICKEL_CHROMIUM_COBALT_ALLOY"
    NICKEL_CHROMIUM_IRON_ALLOY = "NICKEL_CHROMIUM_IRON_ALLOY"
    NICKEL_CHROMIUM_MOLYBDENUM_ALLOY = "NICKEL_CHROMIUM_MOLYBDENUM_ALLOY"
    NICKEL_COBALT_ALLOY = "NICKEL_COBALT_ALLOY"
    NICKEL_COPPER_ALLOY = "NICKEL_COPPER_ALLOY"
    NICKEL_IRON_ALLOY = "NICKEL_IRON_ALLOY"
    NICKEL_MOLYBDENUM_ALLOY = "NICKEL_MOLYBDENUM_ALLOY"
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

    # METAL / STEEL
    ALLOY_STEEL = "ALLOY_STEEL"
    CARBON_STEEL = "CARBON_STEEL"
    LOW_ALLOY_STEEL = "LOW_ALLOY_STEEL"
    MARAGING_STEEL = "MARAGING_STEEL"
    STAINLESS_STEEL = "STAINLESS_STEEL"
    TOOL_AND_MACHINING_STEEL = "TOOL_AND_MACHINING_STEEL"

    # METAL / TITANIUM
    ALPHA_ALLOY = "ALPHA_ALLOY"
    ALPHA_BETA_ALLOY = "ALPHA_BETA_ALLOY"
    BETA_ALLOY = "BETA_ALLOY"
    LOW_ALLOY_TITANIUM = "LOW_ALLOY_TITANIUM"
    NEAR_ALPHA_ALLOY = "NEAR_ALPHA_ALLOY"
    PURE_TITANIUM = "PURE_TITANIUM"

    # POLYMER / ELASTOMER
    CHLOROPOLYETHYLENE = "CHLOROPOLYETHYLENE"
    CHLOROSULFONATED_ETHYLENE = "CHLOROSULFONATED_ETHYLENE"
    EPOXYPRENE = "EPOXYPRENE"
    ETHYLENE_PROPYLENE_DIENE = "ETHYLENE_PROPYLENE_DIENE"
    FLUOROCARBONS = "FLUOROCARBONS"
    FLUOROETHYLENE_PROPYLENE = "FLUOROETHYLENE_PROPYLENE"
    FLUOROSILICONES = "FLUOROSILICONES"
    HYDROGENATED_NITRILE = "HYDROGENATED_NITRILE"
    PERFLUOROCARBONS = "PERFLUOROCARBONS"
    POLYBUTADIENE = "POLYBUTADIENE"
    POLYNORBORNENE = "POLYNORBORNENE"
    POLYTHIOETHERS = "POLYTHIOETHERS"
    RUBBER = "RUBBER"
    TETRAFLUOROETHYLENE_PROPYLENE = "TETRAFLUOROETHYLENE_PROPYLENE"
    THIOKOLS = "THIOKOLS"
    URETHANE = "URETHANE"
    VINYL_METHYL_SILICONE = "VINYL_METHYL_SILICONE"
    VITON = "VITON"

    # POLYMER / THERMOPLASTIC ELASTOMER
    ELASTOMETRIC_ALLOY = "ELASTOMETRIC_ALLOY"
    SYTRENE_BUTADIENE_STYRENE = "STYRENE_BUTADIENE_STYRENE"
    THERMOPLASTIC_COPOLYESTER = "THERMOPLASTIC_COPOLYESTER"
    THERMOPLASTIC_POLYAMIDE = "THERMOPLASTIC_POLYAMIDE"
    THERMOPLASTIC_POLYESTER_ELASTOMER = "THERMOPLASTIC_POLYESTER_ELASTOMER"
    THERMOPLASTIC_POLYOLEFIN = "THERMOPLASTIC_POLYOLEFIN"
    THERMOPLASTIC_POLYURETHANE = "THERMOPLASTIC_POLYURETHANE"
    THERMOPLASTIC_STYRENIC_BLOCK_COPOLYMER = "THERMOPLASTIC_STYRENIC_BLOCK_COPOLYMER"

    # POLYMER / THERMOPLASTIC
    ACRYLONITRILE_BUTADIENE_STYRENE = "ACRYLONITRILE_BUTADIENE_STYRENE"
    ACRYLONITRILE_STYRENE_ACRYLATE = "ACRYLONITRILE_STYRENE_ACRYLATE"
    ARAMIDE = "ARAMIDE"
    ETHYLENE_TETRAFLUOROETHYLENE_COPOLYMER = "ETHYLENE_TETRAFLUOROETHYLENE_COPOLYMER"
    ETHYLENE_VINYL_ACETATE = "ETHYLENE_VINYL_ACETATE"
    FLUORINATED_ETHYLENE_PROPYLENE = "FLUORINATED_ETHYLENE_PROPYLENE"
    FLUOROPOLYMER = "FLUOROPOLYMER"
    HIGH_IMPACT_POLYSTYRENE = "HIGH_IMPACT_POLYSTYRENE"
    LIQUID_CRYSTAL_POLYMERS = "LIQUID_CRYSTAL_POLYMERS"
    METHACRYLATE_BUTADIENE_STYRENE = "METHACRYLATE_BUTADIENE_STYRENE"
    POLYACRYLONITRILE = "POLYACRYLONITRILE"
    POLYAMIDE = "POLYAMIDE"
    POLYAMIDIMIDE = "POLYAMIDIMIDE"
    POLYARYLETHERKETONE = "POLYARYLETHERKETONE"
    POLYBENZIMIDAZOLE = "POLYBENZIMIDAZOLE"
    POLYBUTENE = "POLYBUTENE"
    POLYBUTYLENE_TEREPHTHALATE = "POLYBUTYLENE_TEREPHTHALATE"
    POLYCARBONATE = "POLYCARBONATE"
    POLYESTER = "POLYESTER"
    POLYETHER_KETONE = "POLYETHER_KETONE"
    POLYETHER_SULFONE = "POLYETHER_SULFONE"
    POLYETHERIMIDE = "POLYETHERIMIDE"
    POLYETHYLENE = "POLYETHYLENE"
    POLYETHYLENE_TEREPHTHALATE = "POLYETHYLENE_TEREPHTHALATE"
    POLYETHYLENE_TEREPHTHALATE_GLYCOL = "POLYETHYLENE_TEREPHTHALATE_GLYCOL"
    POLYGLYCOLICIDE = "POLYGLYCOLICIDE"
    POLYIMIDE = "POLYIMIDE"
    POLYKETONE = "POLYKETONE"
    POLYLACTIC_ACID = "POLYLACTIC_ACID"
    POLYMER_BLEND = "POLYMER_BLEND"
    POLYMETHYL_METHACRYLATE = "POLYMETHYL_METHACRYLATE"
    POLYMETHYLPENTENE = "POLYMETHYLPENTENE"
    POLYOLEFIN = "POLYOLEFIN"
    POLYOXYMETHYLENE = "POLYOXYMETHYLENE"
    POLYPHENYL = "POLYPHENYL"
    POLYPHENYL_ETHER = "POLYPHENYL_ETHER"
    POLYPHENYLENE_OXIDE = "POLYPHENYLENE_OXIDE"
    POLYPHENYLENE_SULFIDE = "POLYPHENYLENE_SULFIDE"
    POLYPHENYLSULPHONE = "POLYPHENYLSULPHONE"
    POLYPHTHALAMIDE = "POLYPHTHALAMIDE"
    POLYPROPYLENE = "POLYPROPYLENE"
    POLYSACCHARIDE = "POLYSACCHARIDE"
    POLYSTYRENE = "POLYSTYRENE"
    POLYSULPHONE = "POLYSULPHONE"
    POLYSULPHONES = "POLYSULPHONES"
    POLYTETRAFLUOROETHYLENE = "POLYTETRAFLUOROETHYLENE"
    POLYTRIMETHYLENE_TEREPHTHALATE = "POLYTRIMETHYLENE_TEREPHTHALATE"
    POLYVINYL_CHLORIDE = "POLYVINYL_CHLORIDE"
    POLYVINYLIDENEFLUORIDE = "POLYVINYLIDENEFLUORIDE"
    STYRENE = "STYRENE"
    STYRENE_ACRYLONITRILE = "STYRENE_ACRYLONITRILE"
    VINYL = "VINYL"

    # POLYMER  / THERMOSETTING
    AMINO_RESIN = "AMINO_RESIN"
    BISMALEIMIDE = "BISMALEIMIDE"
    EPOXY_RESIN = "EPOXY_RESIN"
    MELAMINE_FORMALDEHYDE = "MELAMINE_FORMALDEHYDE"
    PHENOL_FORMALDEHYDE_RESIN = "PHENOL_FORMALDEHYDE_RESIN"
    PHTHALONITRILE = "PHTHALONITRILE"
    POLYESTER_RESIN = "POLYESTER_RESIN"
    VINYL_ESTER_RESIN = "VINYL_ESTER_RESIN"


class W24MaterialCategory4(str, Enum):

    # METAL / IRON / CAST_IRON
    GRAY_CAST_IRON = "GRAY_CAST_IRON"
    MALLEABLE_CAST_IRON = "MALLEABLE_CAST_IRON"
    NODULAR_CAST_IRON = "NODULAR_CAST_IRON"
    WHITE_CAST_IRON = "WHITE_CAST_IRON"

    # METAL / STEEL / CARBON_STEEL
    LOW_CARBON_STEEL = "LOW_CARBON_STEEL"
    MEDIUM_CARBON_STEEL = "MEDIUM_CARBON_STEEL"
    HIGH_CARBON_STEEL = "HIGH_CARBON_STEEL"

    # POLYMER / ELASTOMER / RUBBER
    ACRYLIC_ETHYLENE_RUBBER = "ACRYLIC_ETHYLENE_RUBBER"
    ACRYLIC_RUBBER = "ACRYLIC_RUBBER"
    ACRYLONITRILE_BUTADIENE_RUBBER = "ACRYLONITRILE_BUTADIENE_RUBBER"
    BROMOBUTYL_RUBBER = "BROMOBUTYL_RUBBER"
    BUTADIENE_RUBBER = "BUTADIENE_RUBBER"
    BUTYL_RUBBER = "BUTYL_RUBBER"
    CHLOROBUTYL_RUBBER = "CHLOROBUTYL_RUBBER"
    CHLOROPRENE_RUBBER = "CHLOROPRENE_RUBBER"
    EPICHLOROHYDRIN_RUBBER = "EPICHLOROHYDRIN_RUBBER"
    ETHYLENE_PROPYLENE_DIENE_RUBBER = "ETHYLENE_PROPYLENE_DIENE_RUBBER"
    ETHYLENE_PROPYLENE_RUBBER = "ETHYLENE_PROPYLENE_RUBBER"
    FLUOROSILICICONE_RUBBER = "FLUOROSILICONE_RUBBER"
    HYPALON_RUBBER = "HYPALON_RUBBER"
    ISOPRENE_RUBBER = "ISOPRENE_RUBBER"
    NATURAL_RUBBER = "NATURAL_RUBBER"
    NEOPRENE_RUBBER = "NEOPRENE_RUBBER"
    NITRILE_RUBBER = "NITRILE_RUBBER"
    SILICONE_RUBBER = "SILICONE_RUBBER"
    SYTRENE_BUTADIENE_RUBBER = "SYTRENE_BUTADIENE_RUBBER"


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

    # ---- OLD WAY ----

    # BLURB
    AUSTENITIC = "AUSTENITIC"
    BLOB = "BLOB"

    DIN17100_1987_12 = "DIN17100:1987-12"
    """ DIN17100:1987-12
    """

    # ---- NEW WAY ----
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
    ISO1874 = "ISO 1874"

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
