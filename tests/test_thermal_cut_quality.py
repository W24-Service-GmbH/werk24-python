import pytest
from pydantic import ValidationError

from werk24.models.thermal_cut_quality import ThermalCutQuality
from werk24.models.v1.roughness import W24RoughnessLabel
from werk24.models.v2.models import Roughness


def test_designation_round_trips_without_conflating_ranges_and_units():
    value = ThermalCutQuality(perpendicularity_range=2, rz5_range=3, tolerance_class=1)
    assert ThermalCutQuality.model_validate_json(value.model_dump_json()) == value
    assert value.model_dump() == {
        "standard": "ISO 9013", "perpendicularity_range": 2,
        "rz5_range": 3, "tolerance_class": 1,
    }


def test_standard_alone_does_not_infer_quality():
    assert ThermalCutQuality().model_dump() == {
        "standard": "ISO 9013", "perpendicularity_range": None,
        "rz5_range": None, "tolerance_class": None,
    }


@pytest.mark.parametrize("model", [W24RoughnessLabel, Roughness])
def test_new_field_is_optional_for_existing_payloads(model):
    field = model.model_fields["thermal_cut_quality"]
    assert not field.is_required()
    assert field.default is None
    assert model.model_json_schema()["properties"]["thermal_cut_quality"]["default"] is None


@pytest.mark.parametrize("field", ["perpendicularity_range", "rz5_range", "tolerance_class"])
@pytest.mark.parametrize("value", [-1, 10])
def test_designation_components_are_single_digits(field, value):
    with pytest.raises(ValidationError):
        ThermalCutQuality(**{field: value})
