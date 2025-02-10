# from werk24.models.v1 import unit as unit
import importlib
import sys

from .v2 import *  # noqa: F401, F403

# Define the new location of the module

old_packages = [
    "alignment",
    "alphabet",
    "angle",
    "ask",
    "balloon",
    "base_feature",
    "bend",
    "bom_table",
    "chamfer",
    "complexity",
    "date",
    "depth",
    "file_format",
    "font",
    "fraction",
    "gdt",
    "gender",
    "general_tolerances",
    "geometric_shape",
    "helpdesk",
    "hole_feature",
    "icon",
    "language",
    "leader",
    "location",
    "material",
    "measure",
    "note",
    "paper_size",
    "part_family",
    "position",
    "process",
    "projection_method",
    "radius",
    "revision_table",
    "roughness",
    "shape",
    "size",
    "standard",
    "techread",
    "test_dimension",
    "thread_element",
    "thread",
    "title_block",
    "tolerance",
    "typed_model",
    "unit",
    "value",
    "view",
    "weight",
]

# Import the module dynamically
for c_package in old_packages:
    try:
        new_module_path = f"werk24.models.v1.{c_package}"
        sys.modules[f"werk24.models.{c_package}"] = importlib.import_module(
            new_module_path
        )
    except ModuleNotFoundError as e:
        raise ImportError(
            f"Could not import {new_module_path}. Did you move it?"
        ) from e
