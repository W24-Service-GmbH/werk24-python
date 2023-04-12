from typing import List

from pydantic import BaseModel


class W24Process(BaseModel):
    """Base Model for Processes.

    Attributes:
        blurb (str): Name of the process.

        process_category (List[str]): Categorization
            of the process. See DIN 8580 for details.
    """
    blurb: str
    process_category: List[str]
