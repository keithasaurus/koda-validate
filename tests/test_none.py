import pytest

from koda_validate import OptionalValidator, StringValidator
from koda_validate.none import none_validator
from koda_validate.typedefs import Invalid, Valid


def test_none() -> None:
    assert none_validator("a string") == Invalid(["expected None"])

    assert none_validator(None) == Valid(None)

    assert none_validator(False) == Invalid(["expected None"])


@pytest.mark.asyncio
async def test_none_async() -> None:
    assert await none_validator.validate_async("a string") == Invalid(["expected None"])

    assert await none_validator.validate_async(None) == Valid(None)

    assert await none_validator.validate_async(False) == Invalid(["expected None"])


def test_optional_validator() -> None:
    assert OptionalValidator(StringValidator())(None) == Valid(None)
    assert OptionalValidator(StringValidator())(5) == Invalid(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert OptionalValidator(StringValidator())("okok") == Valid("okok")


@pytest.mark.asyncio
async def test_optional_validator_async() -> None:
    assert await OptionalValidator(StringValidator()).validate_async(None) == Valid(None)
    assert await OptionalValidator(StringValidator()).validate_async(5) == Invalid(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert await OptionalValidator(StringValidator()).validate_async("okok") == Valid(
        "okok"
    )
