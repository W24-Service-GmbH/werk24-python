from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import UUID4, BaseModel, HttpUrl, Json

from .ask import W24Ask


class W24TechreadCommand(BaseModel):
    action: str
    message: Json


class W24TechreadMessageType(str, Enum):
    ASK_PAGE_THUMBNAIL = "ASK_PAGE_THUMBNAIL"
    ASK_SHEET_THUMBNAIL = "ASK_SHEET_THUMBNAIL"
    ASK_SECTIONAL_THUMBNAIL = "ASK_SECTIONAL_THUMBNAIL"
    ASK_TRAIN = "ASK_TRAIN"
    ASK_VARIANT_OVERALL_DIMENSIONS = "ASK_VARIANT_OVERALL_DIMENSIONS"
    TECHREAD_INITIALIZATION_SUCCESS = "TECHREAD_INITIALIZATION_SUCCESS"
    TECHREAD_COMPLETED = "TECHREAD_COMPLETED"
    TECHREAD_STARTED = "TECHREAD_STARTED"
    ERROR_INTERNAL = "ERROR_INTERNAL"


class W24TechreadMessage(BaseModel):
    request_id: Optional[UUID4]
    message_type: W24TechreadMessageType
    payload_dict: Optional[Dict] = None
    payload_url: Optional[HttpUrl] = None
    payload_bytes: Optional[bytes]

    @property
    def message_type_main(self):
        return self.message_type.value.split("_", 1)[0]


class W24TechreadArchitecture(str, Enum):
    """ List of available architectures.
    Beware that chosing a different architecture
    will have effects on both the speed and
    the cost of your request.

    By default only CPU_V1 is available to new users.
    Please talk to us if you have other requirements.
    """

    GPU_V1 = "GPU_V1"


class W24TechreadArchitectureStatus(str, Enum):
    """ List of possible architecture states.
    Most likely you will only care about DEPLOYED
    """

    DEPLOYING = "DEPLOYING"
    DEPLOYED = "DEPLOYED"
    UNDEPLOYING = "UNDEPLOYING"
    UNDEPLOYED = "UNDEPLOYED"


class W24TechreadRequest(BaseModel):
    """ Definition of a W24DrawingReadRequest describing
    (i) the Technical Drawing,
    (ii) the associated 3D-Model (optional),
    (iii) the list of features that shall be extracted,
    (iv) the architecture on which to run the algorithm
    (v) the callback url that shall be called after the
    """

    asks: List[W24Ask] = []
    architecture: W24TechreadArchitecture
    webhook: Optional[HttpUrl] = None
    development_key: str = None
