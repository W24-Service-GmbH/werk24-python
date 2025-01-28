from typing import List

from pydantic import BaseModel


class W24Process(BaseModel):
    """Base Model for Processes.

    Attributes:
    ----------
        blurb (str): Name of the process.

        raw_ocr_blurb: Process Name as it was indicated
            on the drawing. This contains more information
            than the blurb.

        process_type (str): Programmatic name of the
            process.

        process_category (List[str]): Categorization
            of the process. See DIN 8580 for details.
    """

    blurb: str
    raw_ocr_blurb: str = ""
    process_type: str
    process_category: List[str]
