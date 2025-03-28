from enum import Enum


class DepthType(str, Enum):
    """
    Enumeration of depth types for holes and pockets.
    """

    SIZE = "SIZE"
    THROUGH = "THROUGH"
    THROUGH_ALL = "THROUGH_ALL"
    BLIND = "BLIND"


class CurvatureType(str, Enum):
    """Curvature types of Radius"""

    CONCAVE = "CONCAVE"
    CONVEX = "CONVEX"
    PLANE = "PLANE"


class Language(str, Enum):
    """
    Enumeration of supported Languages following
    the ISO/639-2/B bibliographic codes.

    Each entry maps a language name to its corresponding code.
    """

    ALB = "ALB"
    """ Albanian (Shqip) """

    AMH = "AMH"
    """ Amharic (አማርኛ) """

    ARA = "ARA"
    """ Arabic (العربية) """

    ARM = "ARM"
    """ Armenian (Հայերեն) """

    AZE = "AZE"
    """ Azerbaijani (Azərbaycan dili) """

    BOS = "BOS"
    """ Bosnian (Bosanski) """

    BUL = "BUL"
    """ Bulgarian (Български) """

    CAT = "CAT"
    """ Catalan (Català) """

    CHI = "CHI"
    """ Chinese (中文) """

    CZE = "CZE"
    """ Czech (Čeština) """

    DAN = "DAN"
    """ Danish (Dansk) """

    DEU = "DEU"
    """ German (Deutsch) """

    DUT = "DUT"
    """ Dutch (Nederlands) """

    ENG = "ENG"
    """ English (English) """

    EST = "EST"
    """ Estonian (Eesti) """

    FIN = "FIN"
    """ Finnish (Suomi) """

    FRA = "FRA"
    """ French (Français) """

    GEO = "GEO"
    """ Georgian (ქართული) """

    GLE = "GLE"
    """ Irish (Gaeilge) """

    GRE = "GRE"
    """ Greek (Ελληνικά) """

    HEB = "HEB"
    """ Hebrew (עברית) """

    HIN = "HIN"
    """ Hindi (हिन्दी) """

    HRV = "HRV"
    """ Croatian (Hrvatski) """

    HUN = "HUN"
    """ Hungarian (Magyar) """

    ICE = "ICE"
    """ Icelandic (Íslenska) """

    IND = "IND"
    """ Indonesian (Bahasa Indonesia) """

    ITA = "ITA"
    """ Italian (Italiano) """

    JPN = "JPN"
    """ Japanese (日本語) """

    KAZ = "KAZ"
    """ Kazakh (Қазақша) """

    KOR = "KOR"
    """ Korean (한국어) """

    LAV = "LAV"
    """ Latvian (Latviešu) """

    LIT = "LIT"
    """ Lithuanian (Lietuvių) """

    MAC = "MAC"
    """ Macedonian (Македонски) """

    MLT = "MLT"
    """ Maltese (Malti) """

    NOR = "NOR"
    """ Norwegian (Norsk) """

    POL = "POL"
    """ Polish (Polski) """

    POR = "POR"
    """ Portuguese (Português) """

    RUM = "RUM"
    """ Romanian (Română) """

    RUS = "RUS"
    """ Russian (Русский) """

    SLO = "SLO"
    """ Slovak (Slovenčina) """

    SLV = "SLV"
    """ Slovenian (Slovenščina) """

    SPA = "SPA"
    """ Spanish (Español) """

    SRP = "SRP"
    """ Serbian (Српски) """

    SWE = "SWE"
    """ Swedish (Svenska) """

    THA = "THA"
    """ Thai (ไทย) """

    TUR = "TUR"
    """ Turkish (Türkçe) """

    UKR = "UKR"
    """ Ukrainian (Українська) """

    URD = "URD"
    """ Urdu (اردو) """

    VIE = "VIE"
    """ Vietnamese (Tiếng Việt) """

    WEL = "WEL"
    """ Welsh (Cymraeg) """

    ZUL = "ZUL"
    """ Zulu (isiZulu) """


class MaterialCategory1(str, Enum):
    FERROUS_ALLOY = "FERROUS_ALLOY"
    NONFERROUS_ALLOY = "NONFERROUS_ALLOY"
    POLYMER = "POLYMER"
    CERAMIC = "CERAMIC"
    COMPOSITE = "COMPOSITE"
    ORGANIC = "ORGANIC"


class MaterialCategory2(str, Enum):
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


class MaterialCategory3(str, Enum):
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


class RoughnessParameter(str, Enum):
    """
    Enum representing roughness parameters commonly specified in engineering drawings.

    This list includes frequently used parameters categorized by their context
    (e.g., ASME standards, profile parameters, roughness parameters, waviness parameters, etc.).

    Note:
    ----
    - This list is not exhaustive.
    - For any additional parameters, feel free to extend or contact the maintainers.
    """

    # ASME Standards
    AA = "AA"  # Arithmetic Average
    CLA = "CLA"  # Center Line Average
    PVA = "PVA"  # Peak-to-Valley Average
    RMS = "RMS"  # Root Mean Square

    # Profile Parameters
    PA = "Pa"  # Arithmetic Mean Deviation
    PC = "PC"  # Peak Count
    PKU = "Pku"  # Kurtosis
    PP = "Pp"  # Peak Height
    PQ = "Pq"  # Root Mean Square Peak
    PSK = "Psk"  # Skewness
    PT = "Pt"  # Total Profile Height
    PV = "Pv"  # Peak-to-Valley Height
    PY = "Py"  # Mean Height of the Profile Peaks
    PZ = "Pz"  # Maximum Height of the Profile

    # Roughness Parameters
    RA = "Ra"  # Arithmetic Average Roughness (DIN Standard)
    RC = "Rc"  # Mean Height of the Profile
    RKU = "Rku"  # Kurtosis
    RP = "Rp"  # Maximum Profile Peak Height
    RQ = "Rq"  # Root Mean Square Roughness
    RSK = "Rsk"  # Skewness
    RT = "Rt"  # Total Roughness Height
    RV = "Rv"  # Maximum Profile Valley Depth
    RY = "Ry"  # Maximum Profile Height
    RZ = "Rz"  # Average Maximum Profile Height

    # Waviness Parameters
    WA = "Wa"  # Arithmetic Average Waviness
    WC = "Wc"  # Mean Height of the Waviness Profile
    WKU = "Wku"  # Kurtosis
    WP = "Wp"  # Maximum Waviness Peak Height
    WQ = "Wq"  # Root Mean Square Waviness
    WSK = "Wsk"  # Skewness
    WT = "Wt"  # Total Waviness Height
    WV = "Wv"  # Maximum Waviness Valley Depth
    WY = "Wy"  # Mean Height of the Waviness Peaks
    WZ = "Wz"  # Maximum Height of the Waviness Profile

    # N-Grade Roughness
    N = "N"  # N-grade roughness


class IdentifierType(str, Enum):
    """
    Enum representing the types of identifiers supported by Werk24.

    These identifiers are commonly used in engineering drawings, contracts,
    and manufacturing processes to uniquely identify components, documents,
    or stakeholders.

    Attributes:
    ----------
    - ASSEMBLY_NAME: Name of the assembly.
    - ASSEMBLY_NUMBER: Number associated with the assembly.
    - CAGE_CODE: Commercial and Government Entity (CAGE) code.
    - CONTRACT_NUMBER: Number associated with a specific contract.
    - CUSTOMER_NAME: Name of the customer.
    - CUSTOMER_NUMBER: Identifier assigned to the customer.
    - DOCUMENT_NUMBER: Identifier for a document.
    - DRAWING_NUMBER: Identifier for a drawing.
    - ERP_NUMBER: Enterprise Resource Planning (ERP) identifier.
    - IDENTIFICATION_NUMBER: General identification number.
    - ITEM_NUMBER: Number assigned to an item (corrected from "ITEM_NUMER").
    - MANUFACTURER_NAME: Name of the manufacturer.
    - MANUFACTURER_NUMBER: Identifier assigned to the manufacturer.
    - MISCELLANEOUS: Miscellaneous identifier.
    - NUMBER: Generic number.
    - ORDER_NAME: Name associated with an order.
    - ORDER_NUMBER: Number associated with an order.
    - REPLACED_BY: Identifier for the component that replaces another.
    - REPLACEMENT_FOR: Identifier for the component that is replaced by another.
    """

    ASSEMBLY_NAME = "ASSEMBLY_NAME"
    ASSEMBLY_NUMBER = "ASSEMBLY_NUMBER"
    CAGE_CODE = "CAGE_CODE"
    CONTRACT_NUMBER = "CONTRACT_NUMBER"
    CUSTOMER_NAME = "CUSTOMER_NAME"
    CUSTOMER_NUMBER = "CUSTOMER_NUMBER"
    DOCUMENT_NUMBER = "DOCUMENT_NUMBER"
    DRAWING_NUMBER = "DRAWING_NUMBER"
    ERP_NUMBER = "ERP_NUMBER"
    IDENTIFICATION_NUMBER = "IDENTIFICATION_NUMBER"
    ITEM_NUMBER = "ITEM_NUMBER"  # Corrected typo
    MANUFACTURER_NAME = "MANUFACTURER_NAME"
    MANUFACTURER_NUMBER = "MANUFACTURER_NUMBER"
    MISCELLANEOUS = "MISCELLANEOUS"
    NUMBER = "NUMBER"
    PART_NUMBER = "PART_NUMBER"
    PRODUCT_GROUP = "PRODUCT_GROUP"
    ORDER_NAME = "ORDER_NAME"
    ORDER_NUMBER = "ORDER_NUMBER"
    REPLACED_BY = "REPLACED_BY"
    REPLACEMENT_FOR = "REPLACEMENT_FOR"


class IdentifierStakeholder(str, Enum):
    """
    Enum representing the types of stakeholders that can be identified by Werk24.

    Stakeholders play distinct roles in the lifecycle of a product, document,
    or process. This enumeration classifies the primary stakeholders.

    Attributes:
    ----------
    - SUPPLIER: The entity supplying the part.
    - OWNER: Owner of the drawing.
    - CUSTOMER: entity requesting the part.
    """

    SUPPLIER = "SUPPLIER"  # The entity supplying the part
    OWNER = "OWNER"  # Owner of the drawing
    CUSTOMER = "CUSTOMER"  # The entity requesting the part


class IdentifierPeriod(str, Enum):
    """
    Enum representing the period of an identifier.

    Attributes:
    ----------
    - PREVIOUS: Refers to a past period or version of the identifier.
    - CURRENT: Refers to the present or active period of the identifier.
    - FUTURE: Refers to a future or planned version of the identifier.
    """

    PREVIOUS = "PREVIOUS"  # Past period or version
    CURRENT = "CURRENT"  # Present or active period
    FUTURE = "FUTURE"  # Future or planned version


class GeneralTolerancesStandard(str, Enum):
    """
    Enum representing all supported general tolerance standards.

    These standards define acceptable limits of variation in dimensions,
    typically applied to mechanical parts and technical drawings.

    Attributes:
    - DIN_7168: General tolerances for linear dimensions (DIN 7168 standard).
    - ISO_2768: General tolerances for linear dimensions and angular dimensions (ISO 2768 standard).
    - ISO_4759_1: General tolerances for fasteners (ISO 4759-1 standard).
    - TOLERANCE_NOTE: A custom or specific tolerance note included in the drawing.
    """

    DIN_7168 = "DIN 7168"  # General tolerances for linear dimensions (DIN standard)
    ISO_2768 = "ISO 2768"  # General tolerances for linear and angular dimensions (ISO standard)
    ISO_4759_1 = "ISO 4759-1"  # General tolerances for fasteners (ISO standard)
    TOLERANCE_NOTE = "TOLERANCE_NOTE"  # Custom or specific tolerance note


class GeneralTolerancesPrinciple(str, Enum):
    """
    Enum representing the supported general tolerance principles.

    These principles define how tolerances are applied and interpreted
    in technical drawings and mechanical part designs.

    Attributes:
    ----------
    - INDEPENDENCE: The independence principle (ISO 8015), where tolerances on
      size and form are treated separately unless explicitly stated.
    - ENVELOPE: The envelope principle (ISO 14405-1), where size and form tolerances
      are combined, ensuring that the surface fits within an ideal envelope.
    """

    INDEPENDENCE = "INDEPENDENCE"  # Tolerances on size and form are treated separately.
    ENVELOPE = "ENVELOPE"  # Tolerances on size and form are combined.


class PageType(str, Enum):
    """
    Enum representing page types
    """

    COMPONENT_DRAWING = "COMPONENT_DRAWING"
    MISCELLANEOUS = "MISCELLANEOUS"


class SizeType(str, Enum):
    """
    Enumeration class for W24 size types.

    Represents different types of sizes that can be used for dimensions in
    engineering and technical contexts.

    Attributes:
    ----------
    - ANGULAR (str): Represents angular sizes or measurements (e.g., angles).
    - LINEAR (str): Represents linear sizes or measurements (e.g., lengths).
    - DIAMETER (str): Represents circular diameter measurements.
    - SPHERICAL_DIAMETER (str): Represents spherical diameter measurements.
    - WIDTH_ACROSS_FLATS (str): Represents the width across flats for hexagonal or similar shapes.
    - SQUARE (str): Represents dimensions of square shapes.
    """

    ANGULAR = "ANGULAR"
    """ Represents angular sizes or measurements. """

    LINEAR = "LINEAR"
    """ Represents linear sizes or measurements. """

    DIAMETER = "DIAMETER"
    """ Represents circular diameter measurements. """

    SPHERICAL_DIAMETER = "SPHERICAL_DIAMETER"
    """ Represents spherical diameter measurements. """

    WIDTH_ACROSS_FLATS = "WIDTH_ACROSS_FLATS"
    """ Represents the width across flats for hexagonal or similar shapes. """

    SQUARE = "SQUARE"
    """ Represents dimensions of square shapes. """


class ThreadHandedness(str, Enum):
    """
    Enumeration describing the direction of a thread.

    Attributes:
    ----------
    - LEFT (str): Indicates a left-handed thread, which tightens counterclockwise.
    - RIGHT (str): Indicates a right-handed thread, which tightens clockwise.
    """

    LEFT = "LEFT"
    """ Indicates a left-handed thread, which tightens counterclockwise. """

    RIGHT = "RIGHT"
    """ Indicates a right-handed thread, which tightens clockwise. """


class ThreadType(str, Enum):
    """Enum for the individual thread types

    NOTE: UTS_COARSE, UTS_FINE, UTS_EXTRAFINE and UTS_SPECIAL
        as individual types will be deprecated. Their information
        individual `threads_per_inch` information will be stored
        in the corresponding variable.
    """

    ISO_METRIC = "ISO_METRIC"
    WHITWORTH = "WHITWORTH"
    UTS = "UTS"
    SM = "SM"
    NPT = "NPT"
    ACME = "ACME"
    KNUCKLE = "KNUCKLE"


class RoughnessStandard(str, Enum):
    """Most standards that define the surface roughness use
    very similar symbols. However, the position of the fields
    varies.

    The standards listed here are understood and supported
    by the API.

    NOTE: the ISO 1302 standard exists in four different versions,
    these releases substantially modified the position and
    structure of the roughness symbols.

    NOTE: this list is not exhaustive, many countries have specified
    their own standards over the years. Do not hesitate to reach
    out if you wish us to implement another standard.

    """

    ISO_1302_1978 = "ISO 1302:1978"
    ISO_1302_1992 = "ISO 1302:1992"
    ISO_1302_2002 = "ISO 1302:2002"
    ISO_21920_1_2021 = "ISO 21920-1:2021"
    ASME_Y14_36_1978 = "ASME Y14.36-1978"
    ASME_Y14_36M_1996 = "ASME Y14.36M-1996"
    ASME_Y14_36_2018 = "ASME Y14.36-2018"
    VARIABLE = "VARIABLE"


class RoughnessMaterialRemovalType(str, Enum):
    """Most standard allow the designer to specify
    whether material removal is required or prohibited.

    By default both options are allowed.
    """

    UNSPECIFIED = "UNSPECIFIED"
    PROHIBITED = "PROHIBITED"
    REQUIRED = "REQUIRED"


class RoughnessDirectionOfLay(str, Enum):
    """The lay of the roughness limits the
    manufacturing process and is sometimes
    required for the application.
    """

    PARALLEL = "="
    PERPENDICULAR = "⟂"
    CROSS = "X"
    MULTIDIRECTIONAL = "M"
    CIRCULAR = "C"
    RADIAL = "R"
    PROTUBERANT = "P"


class RoughnessConditionType(str, Enum):
    """
    Enum representing the type of roughness condition specified on a surface.

    This classification indicates whether the roughness applies to the upper limit,
    lower limit, or average value of the measured surface profile.

    Attributes:
    ----------
    - UPPER: Represents the upper limit of the roughness.
    - LOWER: Represents the lower limit of the roughness.
    - AVERAGE: Represents the average value of the roughness.
    """

    UPPER = "UPPER"  # Upper limit of the roughness
    LOWER = "LOWER"  # Lower limit of the roughness
    AVERAGE = "AVERAGE"  # Average value of the roughness


class RoughnessFilterType(str, Enum):
    """
    Enum representing filter types used during roughness measurement.

    Different filters influence the roughness measurements by emphasizing
    or attenuating specific frequency components of the surface profile.
    This enum allows designers to specify the desired filter to ensure
    consistent and comparable results.
    """

    GAUSSIAN = "G"
    ROBUST_GAUSSIAN = "RG"
    SPLINE = "S"
    TWO_RC = '"2RC"'


class RoughnessAcceptanceCriterion(str, Enum):
    """The designer can specify whether to apply
    the 16%-rule, the maximum- or medium- rule
    when deciding whether a surface complies with
    the specifications.
    """

    SIXTEEN_PERCENT = "16%"
    MAXIMUM = "max"
    MEAN = "mean"


class GDnTCharacteristic(str, Enum):
    """
    Enumeration of possible Geometric Dimensioning and Tolerancing (GD&T) characteristics
    as defined by ISO 1101.

    Attributes:
    ----------
    - ANGULARITY: Angularity (∠), ensures the feature is at a specified angle.
    - CIRCULAR_RUNOUT: Circular runout (↗), controls the surface elements' variation relative to a rotation axis.
    - CIRCULARITY: Circularity (○), ensures the feature is uniformly circular.
    - CONCENTRICITY: Concentricity (◎), ensures the center axes of features are aligned.
    - CYLINDRICITY: Cylindricity (⌭), ensures the feature is uniformly cylindrical.
    - DATUM: Datum indicator ([DATUM]), denotes the location of a reference datum.
    - FLATNESS: Flatness (⏥), ensures the surface is uniformly flat.
    - PARALLELISM: Parallelism (∥), ensures the feature is parallel to a reference.
    - PERPENDICULARITY: Perpendicularity (⟂), ensures the feature is at a 90° angle.
    - POSITION: Position (⌖), defines the allowable location of a feature.
    - PROFILE_OF_A_LINE: Profile of a line (⌒), defines the allowable deviation of a line profile.
    - PROFILE_OF_A_SURFACE: Profile of a surface (⌓), defines the allowable deviation of a surface profile.
    - STRAIGHTNESS: Straightness (⏤), ensures the surface or feature is straight.
    - SYMMETRY: Symmetry (⌯), ensures the feature is symmetric about a reference axis or plane.
    - TOTAL_RUNOUT: Total runout (⌰), controls the surface's variation in all directions relative to a rotation axis.
    """

    ANGULARITY = "∠"  # Angularity
    CIRCULAR_RUNOUT = "↗"  # Circular runout
    CIRCULARITY = "○"  # Circularity
    CONCENTRICITY = "◎"  # Concentricity
    CYLINDRICITY = "⌭"  # Cylindricity
    DATUM = "[DATUM]"  # Datum indicator
    FLATNESS = "⏥"  # Flatness
    PARALLELISM = "∥"  # Parallelism
    PERPENDICULARITY = "⟂"  # Perpendicularity
    POSITION = "⌖"  # Position
    PROFILE_OF_A_LINE = "⌒"  # Profile of a line
    PROFILE_OF_A_SURFACE = "⌓"  # Profile of a surface
    STRAIGHTNESS = "⏤"  # Straightness
    SYMMETRY = "⌯"  # Symmetry
    TOTAL_RUNOUT = "⌰"  # Total runout


class GDnTZoneCombination(str, Enum):
    """
    Enum for tolerance zone combinations as per ISO 1101.

    Attributes:
    ----------
    - COMBINED (CZ): Combines multiple tolerance zones into a single requirement.
    - SEPARATED (SZ): Keeps multiple tolerance zones independent of each other.
    """

    COMBINED = "CZ"
    SEPARATED = "SZ"


class GDnTZoneConstraint(str, Enum):
    """
    Enum for tolerance zone constraints.

    Attributes:
    ----------
    - UNSPECIFIED_INCLINATION (OZ): Tolerance zone inclination is unspecified.
    - UNSPECIFIED_OFFSET (VA): Tolerance zone offset is unspecified.
    - ORIENTATION_ONLY (><): Tolerance zone applies to orientation constraints only.
    """

    UNSPECIFIED_INCLINATION = "OZ"
    UNSPECIFIED_OFFSET = "VA"
    ORIENTATION_ONLY = "><"


class GDnTFilterType(str, Enum):
    """
    Enum for feature filters in geometric tolerancing.

    Filters are applied to measured data to derive meaningful interpretations of tolerances.

    Attributes:
    ----------
    - GAUSSIAN (G): Standard Gaussian filter.
    - SPLINE (S): Spline filter for smoother curves.
    - SPLINE_WAVELET (SW): Wavelet-based spline filter.
    - COMPLEX_WAVELET (CW): Advanced complex wavelet filter.
    - ROBUST_GAUSSIAN (RG): Gaussian filter with robustness improvements.
    - ROBUST_SPLINE (RS): Robust spline filter for challenging data.
    - FOURIER (F): Fourier-based filtering for frequency domain analysis.
    - HULL (H): Convex hull filter for geometrical boundaries.
    """

    GAUSSIAN = "G"
    SPLINE = "S"
    SPLINE_WAVELET = "SW"
    COMPLEX_WAVELET = "CW"
    ROBUST_GAUSSIAN = "RG"
    ROBUST_SPLINE = "RS"
    FOURIER = "F"
    HULL = "H"


class GDnTAssociatedFeature(str, Enum):
    """
    Enum of associated features for geometric tolerancing.

    Attributes:
    ----------
    - MINIMAX (Ⓒ): Minimax feature tolerance.
    - GAUSSIAN (Ⓖ): Gaussian feature tolerance.
    - MIN_CIRCUMSCRIBED (Ⓝ): Minimum circumscribed feature.
    - MAX_CIRCUMSCRIBED (Ⓧ): Maximum circumscribed feature.
    - TANGENT (Ⓣ): Tangent feature tolerance.
    """

    MINIMAX = "Ⓒ"
    GAUSSIAN = "Ⓖ"
    MIN_CIRCUMSCRIBED = "Ⓝ"
    MAX_CIRCUMSCRIBED = "Ⓧ"
    TANGENT = "Ⓣ"


class GDnTDerivedFeature(str, Enum):
    """
    Enum for derived geometric tolerancing features.

    Attributes:
    ----------
    - PROJECTED (Ⓟ): Indicates tolerance for a projected feature.
    - MEAN (Ⓐ): Indicates tolerance for a mean or averaged feature.
    """

    PROJECTED = "Ⓟ"
    MEAN = "Ⓐ"


class GDnTReferenceParameter(str, Enum):
    """
    Enum for reference parameters in geometric tolerancing.

    Attributes:
    ----------
    - PEAK_VALUE (P): Highest value in the tolerance range.
    - VALLEY_VALUE (V): Lowest value in the tolerance range.
    - DEVIATION_SPAN (T): Total deviation span.
    - STANDARD_DEVIATION (Q): Root mean square deviation.
    """

    PEAK_VALUE = "P"
    VALLEY_VALUE = "V"
    DEVIATION_SPAN = "T"
    STANDARD_DEVIATION = "Q"


class GDnTState(str, Enum):
    """
    Enum for GD&T state definitions.

    Attributes:
    ----------
    - FREE (Ⓕ): Indicates that the feature is free without constraints.
    """

    FREE = "Ⓕ"


class GDnTMaterialCondition(str, Enum):
    """
    Enum for material condition modifiers in GD&T.

    Attributes:
    ----------
    - MAXIMUM (Ⓜ): Maximum material condition (MMC).
    - MINIMUM (Ⓛ): Minimum material condition (LMC).
    - RECIPROCITY (Ⓡ): Reciprocity condition.
    """

    MAXIMUM = "Ⓜ"
    MINIMUM = "Ⓛ"
    RECIPROCITY = "Ⓡ"


class GDnTReferenceAssociation(str, Enum):
    """
    Enum for associations of reference elements in geometric dimensioning and tolerancing (GD&T).

    This class defines the various types of reference elements used to evaluate tolerances,
    including unconstrained and constrained minimax (Tschebyschew) and Gaussian elements,
    as well as circumscribed elements.

    Attributes:
    ----------
    - MINIMAX (C): Unconstrained Tschebyschew element, minimizing the maximum deviation.
    - MINIMAX_EXTERNAL (CE): Tschebyschew element with an external constraint.
    - MINIMAX_INTERNAL (CI): Tschebyschew element with an internal constraint.
    - GAUSSIAN (G): Unconstrained Gaussian least squares element.
    - GAUSSIAN_EXTERNAL (GE): Gaussian least squares element with an external constraint.
    - GAUSSIAN_INTERNAL (GI): Gaussian least squares element with an internal constraint.
    - MIN_CIRCUMSCRIBED (N): Minimal circumscribed element, fitting the smallest boundary.
    - MAX_CIRCUMSCRIBED (X): Maximal circumscribed element, fitting the largest boundary.
    """

    MINIMAX = "C"
    """ Unconstrained Tschebyschew element, minimizing the maximum deviation. """

    MINIMAX_EXTERNAL = "CE"
    """ Tschebyschew element with an external constraint. """

    MINIMAX_INTERNAL = "CI"
    """ Tschebyschew element with an internal constraint. """

    GAUSSIAN = "G"
    """ Unconstrained Gaussian least squares element. """

    GAUSSIAN_EXTERNAL = "GE"
    """ Gaussian least squares element with an external constraint. """

    GAUSSIAN_INTERNAL = "GI"
    """ Gaussian least squares element with an internal constraint. """

    MIN_CIRCUMSCRIBED = "N"
    """ Minimal circumscribed element, fitting the smallest boundary. """

    MAX_CIRCUMSCRIBED = "X"
    """ Maximal circumscribed element, fitting the largest boundary. """


class GeometryType(str, Enum):
    """
    Enum representing the basic geometric shapes of raw material.

    This classification categorizes common material shapes used in the industry.
    It ensures concise and clear boundaries between shapes while considering conventional usage.
    ----------
    """

    CUBOID = "CUBOID"  # Includes SHEET or SLAB
    CYLINDER = "CYLINDER"  # Includes BAR, INGOT, BILLET, or BLOOM


class NoteType(str, Enum):
    """
    Enum to differentiate between various types of notes in technical drawings.

    - Canvas Notes: General notes associated with the overall drawing canvas,
      sometimes referred to as "General Notes". These notes apply broadly and are
      not tied to any specific section.
    - View Notes: Notes specific to a particular section of the drawing,
      but not associated with a leader or callout. Example: "VIEW A".
    """

    CANVAS_NOTE = "CANVAS_NOTE"
    VIEW_NOTE = "VIEW_NOTE"


class RedactionZoneType(str, Enum):
    LOGO = "LOGO"
    PERSONAL_DATA = "PERSONAL_DATA"
    COMPANY_DATA = "COMPANY_DATA"
    KEYWORD = "KEYWORD"


class UnitSystemType(str, Enum):
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


class ProjectionMethodType(str, Enum):
    FIRST_ANGLE = "FIRST_ANGLE"
    THIRD_ANGLE = "THIRD_ANGLE"


class VolumeEstimateType(str, Enum):
    UPPER_BOUND_IGNORING_CAVITIES = "UPPER_BOUND_IGNORING_CAVITIES"


class CoordinateSpace(str, Enum):
    PIXEL_SPACE = "PIXEL_SPACE"
    WORLD_SPACE = "WORLD_SPACE"


class TechreadExceptionLevel(str, Enum):
    """Severity level for the Error

    !!! note
        This is defined for future-compatibility.
        The only value that is currently used is ERROR.
        The INFO level will follow shortly.
    """

    ERROR = "ERROR"
    """ Set when the processing was stopped
    """

    INFO = "INFO"
    """ Set when the process was completed successfully,
    but we want to bring something to your awareness
    (e.g,. that you are using a feature that will soon
    be deprecated)
    """


class AskType(str, Enum):
    """The type of request to be sent to the server."""

    BALLOONS = "BALLOONS"
    CUSTOM = "CUSTOM"
    FEATURES = "FEATURES"
    INSIGHTS = "INSIGHTS"
    META_DATA = "META_DATA"
    REDACTION = "REDACTION"
    REFERENCE_POSITIONS = "REFERENCE_POSITIONS"
    SHEET_IMAGES = "SHEET_IMAGES"
    VIEW_IMAGES = "VIEW_IMAGES"


class ThumbnailFileFormat(str, Enum):
    """The output format of the redacted drawing."""

    PDF = "PDF"
    """The output format is PDF."""

    PNG = "PNG"
    """The output format is PNG."""


class PrimaryProcessType(str, Enum):
    CUTTING = "CUTTING"
    TURNING = "TURNING"
    MILLING = "MILLING"
