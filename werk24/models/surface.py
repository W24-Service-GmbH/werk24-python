from typing import List

from pydantic import BaseModel

from .surface_lay import W24SurfaceLay
from .surface_method import W24SurfaceMethod
from .surface_process import W24SurfaceProcess
from .surface_requirement import W24SurfaceRequirement


class W24Surface(BaseModel):
    """ W24Surface describes the surface attributes that
    are generally specified with a surface symbol (see
    for example DIN EN ISO 1302)
    """
    process: W24SurfaceProcess
    requirements: List[W24SurfaceRequirement] = []
    method: W24SurfaceMethod = None
    lay: W24SurfaceLay = None
