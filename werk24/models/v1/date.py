from datetime import date

from pydantic import BaseModel, field_validator


class W24Date(BaseModel):
    """Date object

    Attributes:
        blurb: Date in ISO 8601 format

        date: Python date object; this will
            automatically be interpreted when
            the object is loaded
    """

    @field_validator("date")
    def date_validator(cls, v: date) -> date:
        return v.isoformat()

    blurb: str

    date: date
