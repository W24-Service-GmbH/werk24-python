from pydantic import BaseModel


class W24Standard(BaseModel):
    """W24 Standard.

    Attributes:
        blurb (str): Blurb of the Standard. This
            indicates the 'standard' way of writing
            the standard, potentially including the part,
            year and month of the publication. Note that
            this information will only be available if
            it was indicated on the drawing.
    """

    blurb: str
