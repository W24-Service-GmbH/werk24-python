import pytest

from werk24 import AskCustom, PostprocessorSlot


def test_postprocessor_slot_default_none():
    ask = AskCustom(custom_id="foo")
    assert ask.postprocessor_slot is None


def test_postprocessor_slot_enum_value():
    ask = AskCustom(custom_id="foo", postprocessor_slot=PostprocessorSlot.GREEN)
    assert ask.postprocessor_slot == PostprocessorSlot.GREEN


def test_postprocessor_slot_invalid_value():
    with pytest.raises(ValueError):
        AskCustom(custom_id="foo", postprocessor_slot="red")

