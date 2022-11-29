import pytest

from koda_validate import OptionalValidator, StringValidator
from koda_validate.base import InvalidType, InvalidVariants
from koda_validate.none import none_validator
from koda_validate.validated import Invalid, Valid


def test_none() -> None:
    assert none_validator("a string") == Invalid(InvalidType(none_validator, type(None)))

    assert none_validator(None) == Valid(None)

    assert none_validator(False) == Invalid(InvalidType(none_validator, type(None)))


@pytest.mark.asyncio
async def test_none_async() -> None:
    assert await none_validator.validate_async("a string") == Invalid(
        InvalidType(none_validator, type(None))
    )

    assert await none_validator.validate_async(None) == Valid(None)

    assert await none_validator.validate_async(False) == Invalid(
        InvalidType(none_validator, type(None))
    )


def test_optional_validator() -> None:
    o_v = OptionalValidator(StringValidator())
    assert o_v(None) == Valid(None)
    assert o_v(5) == Invalid(
        InvalidVariants(
            o_v,
            [
                InvalidType(o_v.validator.validators[0], type(None)),
                InvalidType(o_v.validator.validators[1], str),
            ],
        )
    )
    assert o_v("okok") == Valid("okok")


@pytest.mark.asyncio
async def test_optional_validator_async() -> None:
    o_v = OptionalValidator(StringValidator())
    assert await o_v.validate_async(None) == Valid(None)
    assert await o_v.validate_async(5) == Invalid(
        InvalidVariants(
            o_v,
            [
                InvalidType(o_v.validator.validators[0], type(None)),
                InvalidType(o_v.validator.validators[1], str),
            ],
        )
    )
    assert await o_v.validate_async("okok") == Valid("okok")
