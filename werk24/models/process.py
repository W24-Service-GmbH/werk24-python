from typing import Tuple, Optional
from werk24.models.feature import W24FeatureModel


class W24ProcessCategory1:
    """Main Categories following recommendations of DIN 8580.
    """
    PRIMARY_FORMING = "PRIMARY_FORMING"
    FORMING = "FORMING"
    DISJOINING = "DISJOINING"
    JOINING = "JOINING"
    COATING = "COATING"
    PROPERTY_ALTERATION = "PROPERTY_ALTERATION"


class W24ProcessCategory2:
    """Categories following the recommendations of DIN 8580.
    """

    # PRIMARY_FORMING
    PRIMARY_FORMING_FROM_LIQUID_STATE = "PRIMARY_FORMING_FROM_LIQUID_STATE"
    PRIMARY_FORMING_FROM_PLASTIC_STATE = "PRIMARY_FORMING_FROM_PLASTIC_STATE"
    PRIMARY_FORMING_FROM_PASTY_STATE = "PRIMARY_FORMING_FROM_PASTY_STATE"
    PRIMARY_FORMING_FROM_GRAINY_STATE = "PRIMARY_FORMING_FROM_GRAINY_STATE"
    PRIMARY_FORMING_FROM_FIBROUS_STATE = "PRIMARY_FORMING_FROM_FIBROUS_STATE"
    PRIMARY_FORMING_THROUGH_WELDING = "PRIMARY_FORMING_THROUGH_WELDING"
    PRIMARY_FORMING_FROM_GASEOUS_STATE = "PRIMARY_FORMING_FROM_GASEOUS_STATE"
    PRIMARY_FORMING_FROM_IONIZED_STATE = "PRIMARY_FORMING_FROM_IONIZED_STATE"
    PRIMARY_FORMING_THROUGH_ADDITIVE = "PRIMARY_FORMING_THROUGH_ADDITIVE"

    # FORMING
    PRESSURE_FORMING = "PRESSURE_FORMING"
    TENSILE_COMPRESSION_FORMING = "TENSILE_COMPRESSION_FORMING"
    TENSILE_FORMING = "TENSILE_FORMING"
    BEND_FORMING = "BEND_FORMING"
    SHEAR_FORMING = "SHEAR_FORMING"

    # DISJOINING
    CUTTING = "CUTTING"
    MACHINING_WITH_DEFINED_EDGE = "MACHINING_WITH_DEFINED_EDGE"
    MACHINING_WITH_UNDEFINED_EDGE = "MACHINING_WITH_UNDEFINED_EDGE"
    ABLATION = "ABLATION"
    DISASSEMBLING = "DISASSEMBLING"
    CLEANING = "CLEANING"

    # JOINING
    ASSEMBLING = "ASSEMBLING"
    FILLING = "FILLING"
    PRESSING = "PRESSING"
    JOINING_THROUGH_PRIMARY_FORMING = "JOINING_THROUGH_PRIMARY_FORMING"
    JOINING_THROUGH_FORMING = "JOINING_THROUGH_FORMING"
    JOINING_THROUGH_WELDING = "JOINING_THROUGH_WELDING"
    JOINING_THROUGH_SOLDERING = "JOINING_THROUGH_SOLDERING"
    GLUING = "GLUING"
    TEXTILE_JOINING = "TEXTILE_JOINING"

    # COATING
    COATING_FROM_LIQUID_STATE = "COATING_FROM_LIQUID_STATE"
    COATING_FROM_PLASTIC_STATE = "COATING_FROM_PLASTIC_STATE"
    COATING_FROM_PASTY_STATE = "COATING_FROM_PASTY_STATE"
    COATING_FROM_GRAINY_STATE = "COATING_FROM_GRAINY_STATE"
    COATING_THROUGH_WELDING = "COATING_THROUGH_WELDING"
    COATING_THROUGH_SOLDERING = "COATING_THROUGH_SOLDERING"
    COATING_FROM_GASEOUS_STATE = "COATING_FROM_GASEOUS_STATE"
    COATING_FROM_IONIZED_STATE = "COATING_FROM_IONIZED_STATE"

    # PROPERTY_ALTERATION
    HARDENING_THROUGH_FORMING = "HARDENING_THROUGH_FORMING"
    HEAT_TREATING = "HEAT_TREATING"
    THERMO_MECHANICAL_TREATING = "THERMO_MECHANICAL_TREATING"
    SINTERING = "SINTERING"
    MAGNETIZING = "MAGNETIZING"
    IRRADIATING = "IRRADIATING"
    PHOTO_CHEMICAL_TREATING = "PHOTO_CHEMICAL_TREATING"


class W24ProcessCategory3:
    """Subcategories following the recommendations of DIN 8580.
    """

    # DISJOINING / CUTTING
    GUILLOTINING = "GUILLOTINING"
    KNIFE_EDGE_CUTTING = "KNIFE_EDGE_CUTTING"
    WEDGE_CUTTING = "WEDGE_CUTTING"
    CLEAVING = "CLEAVING"
    TEARING = "TEARING"
    BREAKING = "BREAKING"

    # DISJOINING / MACHINING_WITH_DEFINED_EDGE
    TURNING = "TURNING"
    DRILLING = "DRILLING"
    MILLING = "MILLING"
    PLANING = "PLANING"
    BROACHING = "BROACHING"
    SAWING = "SAWING"
    FILING = "FILING"
    ABRASIVE_BRUSHING = "ABRASIVE_BRUSHING"
    SCRAPING = "SCRAPING"

    # DISJOINING / MACHINING_WITH_UNDEFINED_EDGE
    GRINDING_WITH_ROTATING_TOOL = "GRINDING_WITH_ROTATING_TOOL"
    BELT_GRINDING = "BELT_GRINDING"
    BROACHING_OF_HARDENED_MATERIALS = "BROACHING_OF_HARDENED_MATERIALS"
    HONING = "HONING"
    LAPPING = "LAPPING"
    BLASTING = "BLASTING"
    VIBRATORY_FINISHING = "VIBRATORY_FINISHING"

    # DISJOINING / ABLATION
    THERMAL_ABLATION = "THERMAL_ABLATION"
    CHEMICAL_ABLATION = "CHEMICAL_ABLATION"
    ELECTRO_CHEMICAL_ABLATION = "ELECTRO_CHEMICAL_ABLATION"

    # DISJOINING / DISASSEMBLING
    DISAGGREGATING = "DISAGGREGATING"
    DRAINING = "DRAINING"
    DISCONNECTING_FRICTIONAL_CONNECTIONS = "DISCONNECTING_FRICTIONAL_CONNECTIONS"
    DISAGGREGATING_OF_PRIMARY_JOINING_PARTS = "DISAGGREGATING_OF_PRIMARY_JOINING_PARTS"
    DESOLDERING = "DESOLDERING"
    DISAGGREGATING_TEXTILE_CONNECTIONS = "DISAGGREGATING_TEXTILE_CONNECTIONS"

    # DISJOINING / CLEANING
    BLAST_CLEANING = "BLAST_CLEANING"
    MECHANICAL_CLEANING = "MECHANICAL_CLEANING"
    FLUIDIC_CLEANING = "FLUIDIC_CLEANING"
    SOLVENT_CLEANING = "SOLVENT_CLEANING"
    CHEMICAL_CLEANING = "CHEMICAL_CLEANING"
    THERMAL_CLEANING = "THERMAL_CLEANING"

    # JOINING / ASSEMBLING
    LAYERING = "LAYERING"
    INSERTING = "INSERTING"
    TELESCOPING = "TELESCOPING"
    HOOKING = "HOOKING"
    STRAIGHTENING = "STRAIGHTENING"
    PARTIAL_SPREADING = "PARTIAL_SPREADING"

    # JOINING /  FILLING
    POURING = "POURING"
    IMPREGNATING = "IMPREGNATING"

    # JOINING / PRESSING
    SCREWING = "SCREWING"
    CLAMPING = "CLAMPING"
    CLIPPING = "CLIPPING"
    JOINING_THROUGH_CRIMP_CONNECTION = "JOINING_THROUGH_CRIMP_CONNECTION"
    NAILING = "NAILING"
    WEDGING = "WEDGING"
    INTERLOCKING = "INTERLOCKING"

    # JOINING / JOINING_THROUGH_PRIMARY_FORMING
    FILL_CASTING = "FILL_CASTING"
    EMBEDDING = "EMBEDDING"
    RESIN_CASTING = "RESIN_CASTING"
    ELECTRO_PLATING = "ELECTRO_PLATING"
    CEMENTING = "CEMENTING"

    # JOINING / JOINING_THROUGH_FORMING
    JOINING_THROUGH_FORMING_OF_WIRES = "JOINING_THROUGH_FORMING_OF_WIRES"
    JOINING_THROUGH_FORMING_OF_SHEETS_OR_TUBES \
        = "JOINING_THROUGH_FORMING_OF_SHEETS_OR_TUBES"
    RIVETING = "RIVETING"

    # JOINING / JOINING_THROUGH_WELDING
    COMPRESSED_WELDING = "COMPRESSED_WELDING"
    FUSION_WELDING = "FUSION_WELDING"

    # JOINING / JOINING_THROUGH_SOLDERING
    JOINING_SOFT_SOLDERING = "JOINING_SOFT_SOLDERING"
    JOINING_HARD_SOLDERING = "JOINING_HARD_SOLDERING"

    # JOINING / GLUING
    PHYSICAL_GLUING = "PHYSICAL_GLUING"
    CHEMICAL_GLUING = "CHEMICAL_GLUING"

    # JOINING / TEXTILE_JOINING
    # left open for future implementation when we are entering
    # the textile market.

    # COATING / COATING_FROM_LIQUID_STATE
    HOT_DIP_GALVANIZING = "HOT_DIP_GALVANIZING"
    PAINTING = "PAINTING"
    DYEING = "DYEING"
    ENAMELLING = "ENAMELLING"
    COATING_THROUGH_CASTING = "COATING_THROUGH_CASTING"
    PRINTING = "PRINTING"
    MARKING = "MARKING"

    # COATING / COATING_FROM_PLASTIC_STATE
    PUTTYING = "PUTTYING"

    # COATING / COATING_FROM_PASTY_STATE
    PLASTERING = "PLASTERING"

    # COATING / COATING_FROM_GRAINY_STATE
    WHIRL_SINTERING = "WHIRL_SINTERING"
    ELECTRO_STATIC_COATING = "ELECTRO_STATIC_COATING"
    COATING_THROUGH_THERMAL_SPRAYING = "COATING_THROUGH_THERMAL_SPRAYING"

    # COATING / COATING_THROUGH_WELDING
    COMPRESSED_DEPOSIT_WELDING = "COMPRESSED_DEPOSIT_WELDING"
    FUSION_DEPOSIT_WELDING = "FUSION_DEPOSIT_WELDING"

    # COATING / COATING_THROUGH_SOLDERING
    SOFT_DEPOSIT_SOLDERING = "SOFT_DEPOSIT_SOLDERING"
    HARD_DEPOSIT_SOLDERING = "HARD_DEPOSIT_SOLDERING"

    # COATING / COATING_FROM_GASEOUS_STATE
    VACUUM_DEPOSITION = "VACUUM_DEPOSITION"
    VACUUM_POWDERING = "VACUUM_POWDERING"

    # COATING_FROM_IONIZED_STATE = "COATING_FROM_IONIZED_STATE"
    GALVANIC_COATING = "GALVANIC_COATING"
    CHEMICAL_COATING = "CHEMICAL_COATING"

    # PROPERTY_ALTERATION / HARDENING_THROUGH_FORMING
    PEENING = "PEENING"
    ROLLING = "ROLLING"
    DRAGGING = "DRAGGING"
    FORGING = "FORGING"

    # PROPERTY_ALTERATION / HEAT_TREATING
    ANNEALING = "ANNEALING"
    HARDENING = "HARDENING"
    BAINITING = "BAINITING"
    TEMPERING = "TEMPERING"
    QUENCHING = "QUENCHING"
    FREEZING = "FREEZING"
    THERMO_CHEMICAL_TREATING = "THERMO_CHEMICAL_TREATING"
    CURING = "CURING"

    # PROPERTY_ALTERATION / THERMO_MECHANICAL_TREATING
    AUSTENITFORM_HARDENING = "AUSTENITFORM_HARDENING"
    HOT_ISOSTATIC_PRESSING = "HOT_ISO_STATIC_PRESSING"

    # PROPERTY_ALTERATION / SINTERING
    # no sub categories

    # PROPERTY_ALTERATION / MAGNETIZING
    # no sub categories

    # PROPERTY_ALTERATION / IRRADIATING
    # no sub categories

    # PROPERTY_ALTERATION / PHOTO_CHEMICAL_TREATING
    EXPOSING = "EXPOSING"


W24ProcessCategoryTuple = Tuple[
    Optional[W24ProcessCategory1],
    Optional[W24ProcessCategory2],
    Optional[W24ProcessCategory3]
]


class W24Process(W24FeatureModel):
    """Werk24 Process as identified on the drawing.

    Attributes:
        blurb: String representation of the process
            for human consumption. You should only
            use this value to present it to your
            users, but should not try and parse
            this value - as it might become more
            granular in future releases.

        category: Categorization of the process in
            the process groups outlined in DIN 8580:2022-12
    """
    blurb: str
    category: W24ProcessCategoryTuple
