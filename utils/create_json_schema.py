import sys
import json
from importlib import import_module
from pydantic import BaseModel
from enum import EnumMeta
from typing import Dict, Any
import werk24.models


def get_pydantic_schemata(module) -> Dict[str, Any]:
    schemata = {}
    for model_name in dir(module):
        model = getattr(module, model_name)
        if (
            isinstance(model, type)
            and issubclass(model, BaseModel)
            and model is not BaseModel
        ):
            schema_key = f"{module.__name__}.{model.__name__}"
            schemata[schema_key] = model.schema_json()
        elif isinstance(model, EnumMeta):
            schema_key = f"{module.__name__}.{model.__name__}"
            schemata[schema_key] = json.dumps(
                {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [e.value for e in model],
                    },
                }
            )
    return schemata


def create_json_schema_dump(path: str):
    schemata = {}
    modules = [name for name in dir(werk24.models) if not name.startswith("__")]

    for module_name in modules:
        full_module_name = f"werk24.models.{module_name}"
        try:
            module = import_module(full_module_name)
            schemata.update(get_pydantic_schemata(module))
        except ModuleNotFoundError:
            print(f"Warning: Module {full_module_name} not found.", file=sys.stderr)

    with open(path, "w") as file:
        json.dump(schemata, file, indent=4)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <output_path>")
        sys.exit(1)

    output_path = sys.argv[1]
    create_json_schema_dump(output_path)
