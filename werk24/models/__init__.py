import importlib
import pkgutil
import sys

from . import v1 as v1  # noqa: F403
from .enums import *  # noqa: F403
from .models import *  # noqa: F403


def expose_v1_modules():
    # Define the source module
    BASE_MODULE = "werk24.models.v1"
    TARGET_MODULE = "werk24.models"

    # Dynamically import all submodules from v1 and alias them under werk24.models
    for row in pkgutil.iter_modules(importlib.import_module(BASE_MODULE).__path__):
        name = row[1]
        full_name = f"{BASE_MODULE}.{name}"
        module = importlib.import_module(full_name)

        # Alias the module under werk24.models
        sys.modules[f"{TARGET_MODULE}.{name}"] = module

        # Optional: Add it to locals() for direct attribute access
        locals()[name] = module


expose_v1_modules()
