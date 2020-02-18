from pydantic import BaseModel
from .ask_type import W24AskType


class W24Ask(BaseModel):
    """ Base model for all possible demand
    in a W24Demand
    """
    ask_type: W24AskType
