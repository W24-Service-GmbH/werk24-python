from decimal import Decimal

from werk24 import GeneralTolerances


def test_legacy_general_tolerances_remain_valid():
    parsed = GeneralTolerances.model_validate(
        {
            "reference_id": 1,
            "tolerance_standard": "ISO 2768",
            "tolerance_class": "m",
            "principle": None,
        }
    )
    assert parsed.tolerance_note is None
    assert parsed.tolerance_table == []


def test_tolerance_note_and_rows_round_trip():
    raw = {
        "reference_id": 1,
        "tolerance_standard": "TOLERANCE_NOTE",
        "tolerance_class": "",
        "principle": None,
        "tolerance_note": "Dimensions in inches\n.XX ±.005",
        "tolerance_table": [
            {
                "decimal_places": 2,
                "deviation_min": "-.005",
                "deviation_max": ".005",
                "unit": "inch",
            }
        ],
    }
    parsed = GeneralTolerances.model_validate(raw)
    restored = GeneralTolerances.model_validate_json(parsed.model_dump_json())
    assert restored == parsed
    assert restored.tolerance_note == raw["tolerance_note"]
    assert restored.tolerance_table[0].deviation_max == Decimal(".005")
