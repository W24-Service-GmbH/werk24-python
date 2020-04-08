from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import UUID4, BaseModel, HttpUrl, Json

from .ask import W24Ask, W24AskType


class W24TechreadCommand(BaseModel):
    """ Command that is sent from the client to the Server
    """
    action: str
    message: Json


class W24TechreadMessageType(str, Enum):
    """ Message Type of the message that is sent
    from the server to the client
    """
    ASK = "ASK"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"


class W24TechreadMessageSubtypeError(str, Enum):
    """ Message SubtypeError
    """
    INTERNAL = "INTERNAL"


class W24TechreadMessageSubtypeProgress(str, Enum):
    """ Message Subtype Progress
    """
    INITIALIZATION_SUCCESS = "INITIALIZATION_SUCCESS"
    COMPLETED = "COMPLETED"
    STARTED = "STARTED"


W24TechreadMessageSubtypeAsk = W24AskType


W24TechreadMessageSubtype = Union[W24TechreadMessageSubtypeError,
                                  W24TechreadMessageSubtypeProgress,
                                  W24TechreadMessageSubtypeAsk]


class W24TechreadMessage(BaseModel):
    """ Messages that is sent from the Server to the
    client
    """
    request_id: UUID4
    message_type: W24TechreadMessageType
    message_subtype: W24TechreadMessageSubtype
    payload_dict: Optional[Dict] = None
    payload_url: Optional[HttpUrl] = None
    payload_bytes: Optional[bytes] = None


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
    development_key: Optional[str] = None
