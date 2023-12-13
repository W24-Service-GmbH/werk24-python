""" Material Models
"""
from enum import Enum
from typing import Any, List, Optional, Tuple, Union, Literal
from pydantic import Field
from werk24.models.base_feature import BaseModel, W24BaseFeatureModel
from werk24.models.property.glass_homogeneity import W24PropertyGlassHomogeneityType
from werk24.models.typed_model import W24TypedModel


class W24MaterialCategory1(str, Enum):
    FERROUS_ALLOY = "FERROUS_ALLOY"
    NONFERROUS_ALLOY = "NONFERROUS_ALLOY"
    POLYMER = "POLYMER"
    CERAMIC = "CERAMIC"
    COMPOSITE = "COMPOSITE"
    ORGANIC = "ORGANIC"


class W24MaterialCategory2(str, Enum):
    # FERROUS ALLOYS
    STEEL = "STEEL"
    IRON = "IRON"
    MAGNETIC_OR_ELECTRICAL_MATERIAL = "MAGNETIC_OR_ELECTRICAL_MATERIAL"
    SINTERED_POWDERED_METAL = "SINTERED_POWDERED_METAL"
    WELDING_FILLER_MATERIAL = "WELDING_FILLER_MATERIAL"

    # NONFERROUS ALLOY
    ALUMINUM = "ALUMINUM"
    ANTIMONY = "ANTIMONY"
    BERYLLIUM = "BERYLLIUM"
    BISMUTH = "BISMUTH"
    CADMIUM = "CADMIUM"
    CHROMIUM = "CHROMIUM"
    COBALT = "COBALT"
    COPPER = "COPPER"
    GALLIUM = "GALLIUM"
    IRIDIUM = "IRIDIUM"
    LEAD = "LEAD"
    MAGNESIUM = "MAGNESIUM"
    MANGANESE = "MANGANESE"
    MERCURY = "MERCURY"
    MOLYBDENUM = "MOLYBDENUM"
    NICKEL = "NICKEL"
    NIOBIUM = "NIOBIUM"
    PLATINUM = "PLATINUM"
    REAR_EARTHS = "REAR_EARTHS"
    SELENIUM = "SELENIUM"
    SILICON = "SILICON"
    TANTALUM = "TANTALUM"
    THALLIUM = "THALLIUM"
    TIN = "TIN"
    TITANIUM = "TITANIUM"
    TUNGSTEN = "TUNGSTEN"
    VANADIUM = "VANADIUM"
    ZINC = "ZINC"
    ZIRCONIUM = "ZIRCONIUM"

    # POLYMER
    THERMOPLAST = "THERMOPLAST"
    THERMOSET = "THERMOSET"
    THERMOPLASTIC_ELASTOMER = "THERMOPLASTIC_ELASTOMER"
    THERMOSET_ELASTOMER = "THERMOSET_ELASTOMER"
    POLYMER_FOAM = "POLYMER_FOAM"

    # CERAMIC
    REFRACTORY = "REFRACTORY"
    TECHNICAL_CERAMIC = "TECHNICAL_CERAMIC"
    CERAMIC_FOAM = "CERAMIC_FOAM"

    # COMPOSITE
    MATRIX = "MATRIX"
    REINFORCEMENT = "REINFORCEMENT"

    # ORGANIC
    WOOD = "WOOD"


class W24MaterialCategory3(str, Enum):
    # FERROUS_ALLOY / STEEL
    STRUCTURAL_OR_CONSTRUCTIONAL_STEEL = "STRUCTURAL_OR_CONSTRUCTIONAL_STEEL"
    STAINLESS_STEEL = "STAINLESS_STEEL"
    TOOL_STEEL = "TOOL_STEEL"
    CAST_STEEL = "CAST_STEEL"

    # FERROUS_ALLOY / IRON
    CAST_IRON = "CAST_IRON"
    FERROALLOY = "FERROALLOY"

    # POLYMER / THERMOPLAST
    ABS = "ABS"
    ABS_PC = "ABS_PC"
    ABS_PLUS_PA = "ABS_PLUS_PA"
    ABS_PLUS_PA6 = "ABS_PLUS_PA6"
    ABS_PLUS_PA66 = "ABS_PLUS_PA66"
    ABS_PLUS_PBT = "ABS_PLUS_PBT"
    ABS_PLUS_PC = "ABS_PLUS_PC"
    ABS_PLUS_PET = "ABS_PLUS_PET"
    ABS_PLUS_PMMA = "ABS_PLUS_PMMA"
    ABS_PLUS_PVC = "ABS_PLUS_PVC"
    ABS_PLUS_PVC_C = "ABS_PLUS_PVC_C"
    ABS_PLUS_SAN = "ABS_PLUS_SAN"
    ABS_PLUS_TPE = "ABS_PLUS_TPE"
    ABS_PLUS_TPES = "ABS_PLUS_TPES"
    ABS_PLUS_TPU = "ABS_PLUS_TPU"
    ABS_PP = "ABS_PP"
    ACPES = "ACPES"
    AES = "AES"
    AES_PLUS_PC = "AES_PLUS_PC"
    ASA = "ASA"
    ASA_PC = "ASA_PC"
    ASA_PLUS_ABS = "ASA_PLUS_ABS"
    ASA_PLUS_AES = "ASA_PLUS_AES"
    ASA_PLUS_MSAN = "ASA_PLUS_MSAN"
    ASA_PLUS_PA = "ASA_PLUS_PA"
    ASA_PLUS_PC = "ASA_PLUS_PC"
    ASA_PLUS_PMMA = "ASA_PLUS_PMMA"
    ASA_PLUS_SAN = "ASA_PLUS_SAN"
    ASA_PLUS_TPE = "ASA_PLUS_TPE"
    BMI = "BMI"
    BVOH = "BVOH"
    CAB = "CAB"
    CAP = "CAP"
    CE = "CE"
    COC = "COC"
    CP = "CP"
    CPE = "CPE"
    CPT = "CPT"
    E_P = "E_P"
    EA = "EA"
    EAA = "EAA"
    EBA = "EBA"
    EBACO = "EBACO"
    EC = "EC"
    ECTFE = "ECTFE"
    EEA = "EEA"
    EFEP = "EFEP"
    EMAA = "EMAA"
    EMAAA = "EMAAA"
    ENBAGMA = "ENBAGMA"
    ETFE = "ETFE"
    EVA = "EVA"
    EVACO = "EVACO"
    EVOH = "EVOH"
    FEP = "FEP"
    HDPE = "HDPE"
    HIPP = "HIPP"
    HIPS = "HIPS"
    IONOMER_RESIN = "IONOMER_RESIN"
    LCP = "LCP"
    LCP_PLUS_PPS = "LCP_PLUS_PPS"
    LDPE = "LDPE"
    LDPE_EVA = "LDPE_EVA"
    LDPE_LLDPE = "LDPE_LLDPE"
    LLDPE = "LLDPE"
    LMDPE = "LMDPE"
    MABS = "MABS"
    MBS = "MBS"
    MDPE = "MDPE"
    MFA = "MFA"
    PA = "PA"
    PA_MACM10_1010 = "PA_MACM10_1010"
    PA_MACM12 = "PA_MACM12"
    PA_MACM12_PLUS_PA_12 = "PA_MACM12_PLUS_PA_12"
    PA_MXD6 = "PA_MXD6"
    PA_MXD6_MXDI = "PA_MXD6_MXDI"
    PA_PACM12 = "PA_PACM12"
    PA_PLUS_HDPE = "PA_PLUS_HDPE"
    PA_PLUS_PA66_6 = "PA_PLUS_PA66_6"
    PA_PLUS_PE = "PA_PLUS_PE"
    PA_PLUS_PP = "PA_PLUS_PP"
    PA_PLUS_PPA = "PA_PLUS_PPA"
    PA_PLUS_SPS = "PA_PLUS_SPS"
    PA_PLUS_TPE = "PA_PLUS_TPE"
    PA_TPE = "PA_TPE"
    PA1010 = "PA1010"
    PA1012 = "PA1012"
    PA10T_X = "PA10T_X"
    PA11 = "PA11"
    PA12 = "PA12"
    PA12_MACMI = "PA12_MACMI"
    PA12_MACMI_PLUS_PA12 = "PA12_MACMI_PLUS_PA12"
    PA410 = "PA410"
    PA46 = "PA46"
    PA46_PLUS_PA6 = "PA46_PLUS_PA6"
    PA4T = "PA4T"
    PA510 = "PA510"
    PA6 = "PA6"
    PA6_12 = "PA6_12"
    PA6_3T = "PA6_3T"
    PA6_66_12 = "PA6_66_12"
    PA6_66_136 = "PA6_66_136"
    PA6_66_610 = "PA6_66_610"
    PA6_69 = "PA6_69"
    PA6_6I = "PA6_6I"
    PA6_6T = "PA6_6T"
    PA6_IPDI = "PA6_IPDI"
    PA6_PA12 = "PA6_PA12"
    PA6_PLUS_ASA = "PA6_PLUS_ASA"
    PA6_PLUS_PA_6I_6T = "PA_6_PLUS_PA_6I_6T"
    PA6_PLUS_PA12 = "PA6_PLUS_PA12"
    PA6_PLUS_PA12_X = "PA6_PLUS_PA12_X"
    PA6_PLUS_PA66 = "PA6_PLUS_PA66"
    PA6_PLUS_PA66_6 = "PA6_PLUS_PA66_6"
    PA6_PLUS_PE = "PA6_PLUS_PE"
    PA6_PLUS_PP = "PA6_PLUS_PP"
    PA610 = "PA610"
    PA612 = "PA612"
    PA66 = "PA66"
    PA66_6 = "PA66_6"
    PA66_610 = "PA66_610"
    PA66_PLUS_PA610 = "PA66_PLUS_PA610"
    PA66_PLUS_PA612 = "PA66_PLUS_PA612"
    PA66_PLUS_PA6I = "PA66_PLUS_PA6I"
    PA66_PLUS_PA6I_6T = "PA66_PLUS_PA6I_6T"
    PA66_PLUS_PA6I_X = "PA66_PLUS_PA6I_X"
    PA66_PLUS_PE = "PA66_PLUS_PE"
    PA66_PLUS_PP = "PA66_PLUS_PP"
    PA66_PLUS_PPA = "PA66_PLUS_PPA"
    PA69 = "PA69"
    PA6I = "PA6I"
    PA6I_6T = "PA6I_6T"
    PA6I_X = "PA6I_X"
    PA6T = "PA6T"
    PA6T_66 = "PA6T_66"
    PA6T_XT_PLUS_PA6T_66 = "PA6T_XT_PLUS_PA6T_66"
    PA6T_6I = "PA6T_6I"
    PA6T_6I_66 = "PA6T_6I_66"
    PA6T_MPMDT = "PA6T_MPMDT"
    PA6T_XT = "PA6T_XT"
    PA9T = "PA9T"
    PAEK = "PAEK"
    PAI = "PAI"
    PAMXD6_PA66 = "PAMXD6_PA66"
    PAO = "PAO"
    PAR = "PAR"
    PARA = "PARA"
    PB = "PB"
    PBAT = "PBAT"
    PBAT_PLUS_PLA = "PBAT_PLUS_PLA"
    PBI = "PBI"
    PBS = "PBS"
    PBT = "PBT"
    PBT_ASA = "PBT_ASA"
    PBT_PC = "PBT_PC"
    PBT_PLUS_ASA = "PBT_PLUS_ASA"
    PBT_PLUS_PE = "PBT_PLUS_PE"
    PBT_PLUS_PET = "PBT_PLUS_PET"
    PBT_PLUS_PET_PLUS_ASA = "PBT_PLUS_PET_PLUS_ASA"
    PBT_PLUS_PETG = "PBT_PLUS_PETG"
    PBT_PLUS_PPE = "PBT_PLUS_PPE"
    PBT_PLUS_PS = "PBT_PLUS_PS"
    PBT_PLUS_SAN = "PBT_PLUS_SAN"
    PC = "PC"
    PC_PET = "PC_PET"
    PC_PLUS_HIPS = "PC_PLUS_HIPS"
    PC_PLUS_MBS = "PC_PLUS_MBS"
    PC_PLUS_PBT = "PC_PLUS_PBT"
    PC_PLUS_PCT = "PC_PLUS_PCT"
    PC_PLUS_PET = "PC_PLUS_PET"
    PC_PLUS_PET_PLUS_PBT = "PC_PLUS_PET_PLUS_PBT"
    PC_PLUS_PLA = "PC_PLUS_PLA"
    PC_PLUS_PMMA = "PC_PLUS_PMMA"
    PC_PLUS_PPC = "PC_PLUS_PPC"
    PC_PLUS_PS = "PC_PLUS_PS"
    PC_PLUS_PTFE = "PC_PLUS_PTFE"
    PC_PLUS_SAN = "PC_PLUS_SAN"
    PC_PLUS_TPES = "PC_PLUS_TPES"
    PC_PLUS_TPU = "PC_PLUS_TPU"
    PC_PPC = "PC_PPC"
    PCL = "PCL"
    PCT = "PCT"
    PCTA = "PCTA"
    PCTFE = "PCTFE"
    PCTG = "PCTG"
    PCTG_PLUS_PC = "PCTG_PLUS_PC"
    PE = "PE"
    PE_HMW = "PE_HMW"
    PE_HMWHD = "PE_HMWHD"
    PE_PLUS_HIPS = "PE_PLUS_HIPS"
    PE_UHMW = "PE_UHMW"
    PEEK = "PEEK"
    PEI = "PEI"
    PEI_PLUS_PCE = "PEI_PLUS_PCE"
    PEK = "PEK"
    PEKEKK = "PEKEKK"
    PEKK = "PEKK"
    PEN = "PEN"
    PESU = "PESU"
    PET = "PET"
    PET_G = "PET_G"
    PET_PLUS_PA6 = "PET_PLUS_PA6"
    PET_PLUS_PA66 = "PET_PLUS_PA66"
    PEX_B = "PEX_B"
    PFA = "PFA"
    PFSA_PTFE = "PFSA_PTFE"
    PGA = "PGA"
    PHA = "PHA"
    PHB = "PHB"
    PHBV = "PHBV"
    PI = "PI"
    PIB = "PIB"
    PK = "PK"
    PLA = "PLA"
    PLA_PCL = "PLA_PCL"
    PLA_PEG = "PLA_PEG"
    PLA_PHA = "PLA_PHA"
    PLA_PLUS_ABS = "PLA_PLUS_ABS"
    PLA_PLUS_HDPE = "PLA_PLUS_HDPE"
    PLA_PLUS_PHB = "PLA_PLUS_PHB"
    PLA_PLUS_PMMA = "PLA_PLUS_PMMA"
    PLGA = "PLGA"
    PMMA = "PMMA"
    PMMI = "PMMI"
    PMP = "PMP"
    PMS = "PMS"
    POM = "POM"
    POM_PLUS_MBS = "POM_PLUS_MBS"
    POM_PLUS_PE = "POM_PLUS_PE"
    POM_PLUS_PTFE = "POM_PLUS_PTFE"
    POM_PLUS_PUR = "POM_PLUS_PUR"
    PP = "PP"
    PP_PE = "PP_PE"
    PP_PLUS_EPDM = "PP_PLUS_EPDM"
    PP_PLUS_EPR = "PP_PLUS_EPR"
    PP_PLUS_EVA = "PP_PLUS_EVA"
    PP_PLUS_PE = "PP_PLUS_PE"
    PP_PLUS_PPE_PLUS_PS = "PP_PLUS_PPE_PLUS_PS"
    PPA = "PPA"
    PPC = "PPC"
    PPE = "PPE"
    PPE_PLUS_HIPS = "PPE_PLUS_HIPS"
    PPE_PLUS_PA = "PPE_PLUS_PA"
    PPE_PLUS_PA6 = "PPE_PLUS_PA6"
    PPE_PLUS_PA66 = "PPE_PLUS_PA66"
    PPE_PLUS_PP = "PPE_PLUS_PP"
    PPE_PLUS_PS = "PPE_PLUS_PS"
    PPE_PLUS_PS_PLUS_PA = "PPE_PLUS_PS_PLUS_PA"
    PPE_PLUS_TPE = "PPE_PLUS_TPE"
    PPE_PLUS_TPS_SEBS = "PPE_PLUS_TPS_SEBS"
    PPOX = "PPOX"
    PPS = "PPS"
    PPS_PLUS_PA = "PPS_PLUS_PA"
    PPS_PLUS_PPE = "PPS_PLUS_PPE"
    PPS_PLUS_PTFE = "PPS_PLUS_PTFE"
    PPSU = "PPSU"
    PPSU_PLUS_PSU = "PPSU_PLUS_PSU"
    PS = "PS"
    PS_I = "PS_I"
    PS_PLUS_PE = "PS_PLUS_PE"
    PS_PLUS_PMMA = "PS_PLUS_PMMA"
    PS_PLUS_SPS = "PS_PLUS_SPS"
    PSU = "PSU"
    PSU_PLUS_ABS = "PSU_PLUS_ABS"
    PSU_PLUS_PC = "PSU_PLUS_PC"
    PTFE = "PTFE"
    PTT = "PTT"
    PVAL = "PVAL"
    PVB = "PVB"
    PVC = "PVC"
    PVC_C = "PVC_C"
    PVC_C_PLUS_PVC = "PVC_C_PLUS_PVC"
    PVC_PLUS_NBR = "PVC_PLUS_NBR"
    PVC_PLUS_PMMA = "PVC_PLUS_PMMA"
    PVC_PLUS_PUR = "PVC_PLUS_PUR"
    PVC_U = "PVC_U"
    PVCA = "PVCA"
    PVDC = "PVDC"
    PVDF = "PVDF"
    PVP = "PVP"
    RPS = "RPS"
    SAN = "SAN"
    SB = "SB"
    SMA = "SMA"
    SMA_PLUS_HIPS = "SMA_PLUS_HIPS"
    SMI = "SMI"
    SMMA = "SMMA"
    SPS = "SPS"
    SRP = "SRP"
    TPC_EE_PLUS_PBT = "TPC_EE_PLUS_PBT"
    TPC_ET_PLUS_EMA = "TPC_ET_PLUS_EMA"
    TPC_ET_PLUS_PBT = "TPC_ET_PLUS_PBT"
    TPES = "TPES"
    TPU_PLUS_TPS_PLUS_TPA = "TPU_PLUS_TPS_PLUS_TPA"
    VDF_CTFE = "VDF_CTFE"
    VDF_HFP = "VDF_HFP"
    VINYL_CHLORIDE_BLEND = "VINYL_CHLORIDE_BLEND"
    VLDPE = "VLDPE"
    XLPE = "XLPE"
    XLPO = "XLPO"

    # POLYMER / THERMOSET
    CA = "CA"
    EP = "EP"
    MA = "MA"
    MF = "MF"
    MP = "MP"
    PDAIP = "PDAIP"
    PDAP = "PDAP"
    PUR = "PUR"
    UF = "UF"
    UP = "UP"
    VE = "VE"

    # POLYMER / THERMOPLASTIC_ELASTOMER
    MPR = "MPR"
    PCU = "PCU"
    PEBA = "PEBA"
    SPU = "SPU"
    TPA = "TPA"
    TPC = "TPC"
    TPC_EE = "TPC_EE"
    TPC_ES = "TPC_ES"
    TPC_ET = "TPC_ET"
    TPE = "TPE"
    TPO = "TPO"
    TPO_EB = "TPO_EB"
    TPO_EO = "TPO_EO"
    TPO_EPDM_PLUS_PP = "TPO_EPDM_PLUS_PP"
    TPS = "TPS"
    TPS_SBS = "TPS_SBS"
    TPS_SEBS = "TPS_SEBS"
    TPS_SIS = "TPS_SIS"
    TPU = "TPU"
    TPU_ALES = "TPU_ALES"
    TPU_ALET = "TPU_ALET"
    TPU_ARES = "TPU_ARES"
    TPU_ARET = "TPU_ARET"
    TPU_ES = "TPU_ES"
    TPU_ET = "TPU_ET"
    TPV = "TPV"
    TPV_EPDM = "TPV_EPDM"
    TPV_EPDM_PLUS_PP = "TPV_EPDM_PLUS_PP"
    TPV_IIR_HIIR = "TPV_IIR_HIIR"
    TPV_NBR = "TPV_NBR"
    TSPCU = "TSPCU"
    TSPU = "TSPU"

    # POLYMER / THERMOSET_ELASTOMER
    ACM = "ACM"
    ACSM = "ACSM"
    AEM = "AEM"
    AU = "AU"
    BIIR = "BIIR"
    BR = "BR"
    CIIR = "CIIR"
    CM = "CM"
    CR = "CR"
    CR_NBR = "CR_NBR"
    CR_SBR = "CR_SBR"
    CSM = "CSM"
    ECO = "ECO"
    EPDM = "EPDM"
    EPDM_SBR = "EPDM_SBR"
    EPM = "EPM"
    EPM_EPDM = "EPM_EPDM"
    EPT = "EPT"
    EU = "EU"
    FFKM = "FFKM"
    FKM = "FKM"
    FMQ = "FMQ"
    FVMQ = "FVMQ"
    HNBR = "HNBR"
    IIR = "IIR"
    IR = "IR"
    IR_BR = "IR_BR"
    NBR = "NBR"
    NBR_PVC = "NBR_PVC"
    NBR_SBR = "NBR_SBR"
    NR = "NR"
    PDMS = "PDMS"
    PUMA = "PUMA"
    PVMQ = "PVMQ"
    RET = "RET"
    SBR = "SBR"
    SBR_ACM = "SBR_ACM"
    SBR_BR = "SBR_BR"
    SBR_IR = "SBR_IR"
    SBR_NR = "SBR_NR"
    SI = "SI"
    VMQ = "VMQ"
    VMQ_PVMQ = "VMQ_PVMQ"
    XNBR = "XNBR"
    XNBR_PVC = "XNBR_PVC"

    # COMPOSITE
    CARBON_FIBER_COMPOSITE = "CARBON_FIBER_COMPOSITE"
    GLASS_FIBER_COMPOSITE = "GLASS_FIBER_COMPOSITE"

    # REINFORCEMENT
    FIBER_REINFORCEMENT = "FIBER_REINFORCEMENT"
    STRUCTURAL_COMPOSITE = "STRUCTURAL_COMPOSITE"

    # FOAM / POLYMER_FOAM
    POLYPHENYLENE_OR_POLYSTYRENE = "POLYPHENYLENE_OR_POLYSTYRENE"
    POLYPHENYLENE_OR_POLYSTYRENE_HIPS = "POLYPHENYLENE_OR_POLYSTYRENE_HIPS"
    POLYCARBONATE = "POLYCARBONATE"

    # CERAMIC / REFRACTORY
    ALUMINA_BASED_CERAMIC = "ALUMINA_BASED_CERAMIC"
    CALCIA_BASED_CERAMIC = "CALCIA_BASED_CERAMIC"
    CARBON_BASED_CERAMIC = "CARBON_BASED_CERAMIC"
    CHROMIA_BASED_CERAMIC = "CHROMIA_BASED_CERAMIC"
    MAGNESIA_BASED_CERAMIC = "MAGNESIA_BASED_CERAMIC"
    MONOLOTHIC = "MONOLOTHIC"
    SIC_BASED_CERAMIC = "SIC_BASED_CERAMIC"
    SILICA_BASED_CERAMIC = "SILICA_BASED_CERAMIC"
    ZIRCONIA_BASED_CERAMIC = "ZIRCONIA_BASED_CERAMIC"

    # CERAMIC / TECHNICAL_CERAMIC
    BORIDE_CERAMIC = "BORIDE_CERAMIC"
    CARBIDE_CERAMIC = "CARBIDE_CERAMIC"
    GLASS_CERAMIC = "GLASS_CERAMIC"
    MIXED_CERAMIC = "MIXED_CERAMIC"
    NITRIDE_CERAMIC = "NITRIDE_CERAMIC"
    SILICATE_CERAMIC = "SILICATE_CERAMIC"
    SINGLE_OXIDE_CERAMIC = "SINGLE_OXIDE_CERAMIC"
    TITANATE_CERAMIC = "TITANATE_CERAMIC"

    # CERAMIC / FIBER
    FIBER_CERAMIC = "FIBER_CERAMIC"


class W24MaterialConditionBase(W24TypedModel):
    class Config:
        discriminators: Tuple[str, ...] = ("condition_type",)

    condition_type: str
    blurb: str


class W24AluminumTemper(W24MaterialConditionBase):
    """
    Aluminium Temper

    Following ISO 2107
    """

    condition_type: Literal["ALUMINUM_TEMPER"] = "ALUMINUM_TEMPER"

    blurb: str = Field(
        description="Blurb of the Aluminum Temper",
        examples=["T6", "H32"],
    )


class W24SteelTreatment(W24MaterialConditionBase):
    """
    Steel Treatments

    Following EN 10083
    """

    condition_type: Literal["STEEL_TREATMENT"] = "STEEL_TREATMENT"
    blurb: str = Field(
        description="Blurb of Steel Treatments",
        examples=["+Q"],
    )


class W24GlassHomogeneityCondition(W24MaterialConditionBase):
    """
    Glass Homogeneity Condition
    """

    condition_type: Literal["GLASS_HOMOGENEITY"] = "GLASS_HOMOGENEITY"
    glass_homogeneity: W24PropertyGlassHomogeneityType


""" List of the Material Conditions for the different material types """
W24MaterialCondition = Union[
    W24GlassHomogeneityCondition,
    W24AluminumTemper,
    W24SteelTreatment,
]


class W24Material(W24BaseFeatureModel):
    """W24 Object for Materials.

    Parsed Material object that can either be
    associated to the TitleBlock or derived from
    all the available information (including the
    text on the canvas.

    Attributes:
    ----------
        blurb: Material Name for human consumption.
            This will typically include the designation
            and the standard.

        raw_ocr_blurb: Material Name as it was indicated
            on the drawing. This contains more information
            than the blurb and is also present when the
            material was not found in the internal
            material database.

        standard: Material Standard indicated
            on the technical drawing. This used to be
            an enum - but we now have over 100 supported
            material standards and the number is increasing
            weekly. So a string seems to be more appropriate.

        designation: Name of the material in accordance
            with the material standard. An alternative name
            would be material_designation.

        material_category: Categorization of the material
            following W24MaterialCategoryX Tree.

    """

    blurb: str
    raw_ocr_blurb: str = ""
    standard: str
    designation: str
    material_category: Tuple[
        Optional[W24MaterialCategory1],
        Optional[W24MaterialCategory2],
        Optional[W24MaterialCategory3],
    ]
    material_conditions: list[W24MaterialCondition] = []

    # ! DEPRECATED in version 1.4.0
    material_family: Optional[Any] = None
    material_class: Optional[Any] = None
    material_type: Optional[Any] = None
    material_group: Optional[Any] = None
    material_standard: Any
    material_code: str


class W24MaterialSet(BaseModel):
    """Set of Materials are used when two or more materials are defined
        for a part which are applicable together.

    Args:
    ----
        material (list[W24material]): List of W24Materials that are
            defined together for a part.
            For example,
                Material_A+Material_B+MAterial_C
                Commonly occurs with polymers like PA+PVC+GF

    """

    material: List[W24Material]
    blurb: str
