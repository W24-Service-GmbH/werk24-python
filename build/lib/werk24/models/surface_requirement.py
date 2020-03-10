from pydantic import BaseModel


class W24SurfaceRequirement(BaseModel):
    """ W24SurfaceRequirement contains the information
    on specific requirements on material surfaces.

    NOTE: As these requirements come in a very wide range,
    they are currently only available as blob.
    """

    blob: str
