import pytest
from koda import Err, Ok

from koda_validate import OptionalValidator, StringValidator
from koda_validate.none import none_validator


def test_none() -> None:
    assert none_validator("a string") == Err(["expected None"])

    assert none_validator(None) == Ok(None)

    assert none_validator(False) == Err(["expected None"])


@pytest.mark.asyncio
async def test_none_async() -> None:
    assert await none_validator.validate_async("a string") == Err(["expected None"])

    assert await none_validator.validate_async(None) == Ok(None)

    assert await none_validator.validate_async(False) == Err(["expected None"])


def test_optional_validator() -> None:
    assert OptionalValidator(StringValidator())(None) == Ok(None)
    assert OptionalValidator(StringValidator())(5) == Err(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert OptionalValidator(StringValidator())("okok") == Ok("okok")


@pytest.mark.asyncio
async def test_optional_validator_async() -> None:
    assert await OptionalValidator(StringValidator()).validate_async(None) == Ok(None)
    assert await OptionalValidator(StringValidator()).validate_async(5) == Err(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert await OptionalValidator(StringValidator()).validate_async("okok") == Ok("okok")
