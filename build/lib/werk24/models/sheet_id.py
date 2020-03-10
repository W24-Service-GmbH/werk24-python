import datetime

from pydantic import BaseModel


class W24SheetId(BaseModel):
    """ The W24SheetId object contains the information
    that is frequently used to refer to a specific sheet

    1. The drawing id as quoted on the sheet or on the
        title page
    2. The respective revision id
    3. The date of the drawing
    """

    sheet_id: str = None
    revision: str = None
    date: datetime.date = None
