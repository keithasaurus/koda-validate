import pytest

from koda_validate import OptionalValidator, StringValidator
from koda_validate.base import InvalidType, InvalidVariants
from koda_validate.none import none_validator
from koda_validate.validated import Invalid, Valid


def test_none() -> None:
    assert none_validator("a string") == Invalid(InvalidType(type(None), none_validator))

    assert none_validator(None) == Valid(None)

    assert none_validator(False) == Invalid(InvalidType(type(None), none_validator))


@pytest.mark.asyncio
async def test_none_async() -> None:
    assert await none_validator.validate_async("a string") == Invalid(
        InvalidType(type(None), none_validator)
    )

    assert await none_validator.validate_async(None) == Valid(None)

    assert await none_validator.validate_async(False) == Invalid(
        InvalidType(type(None), none_validator)
    )


def test_optional_validator() -> None:
    o_v = OptionalValidator(StringValidator())
    assert o_v(None) == Valid(None)
    assert o_v(5) == Invalid(
        InvalidVariants(
            [
                InvalidType(type(None), o_v.validator.validators[0]),
                InvalidType(str, o_v.validator.validators[1]),
            ]
        )
    )
    assert o_v("okok") == Valid("okok")


@pytest.mark.asyncio
async def test_optional_validator_async() -> None:
    o_v = OptionalValidator(StringValidator())
    assert await o_v.validate_async(None) == Valid(None)
    assert await o_v.validate_async(5) == Invalid(
        InvalidVariants(
            [
                InvalidType(type(None), o_v.validator.validators[0]),
                InvalidType(str, o_v.validator.validators[1]),
            ]
        )
    )
    assert await o_v.validate_async("okok") == Valid("okok")
