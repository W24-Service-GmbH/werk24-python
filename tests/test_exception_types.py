from werk24.models.v1.techread import W24TechreadExceptionType
from werk24.models.v2.internal import TechreadExceptionType


def test_configuration_incorrect_enum_present():
    assert TechreadExceptionType.CONFIGURATION_INCORRECT.value == "CONFIGURATION_INCORRECT"
    assert W24TechreadExceptionType.CONFIGURATION_INCORRECT.value == "CONFIGURATION_INCORRECT"
