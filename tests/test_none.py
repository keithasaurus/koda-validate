import pytest

from koda_validate import Invalid, OptionalValidator, StringValidator, Valid
from koda_validate.base import TypeErr, VariantErrs
from koda_validate.none import NoneValidator, none_validator


def test_none() -> None:
    assert none_validator("a string") == Invalid(
        none_validator, "a string", TypeErr(type(None))
    )

    assert none_validator(None) == Valid(None)

    assert none_validator(False) == Invalid(none_validator, False, TypeErr(type(None)))


def test_none_repr() -> None:
    assert repr(NoneValidator()) == repr(none_validator) == "NoneValidator()"


def test_none_eq() -> None:
    assert NoneValidator() == NoneValidator() == none_validator
    assert NoneValidator() is NoneValidator() is none_validator


@pytest.mark.asyncio
async def test_none_async() -> None:
    assert await none_validator.validate_async("a string") == Invalid(
        none_validator, "a string", TypeErr(type(None))
    )

    assert await none_validator.validate_async(None) == Valid(None)

    assert await none_validator.validate_async(False) == Invalid(
        none_validator, False, TypeErr(type(None))
    )


def test_optional_validator() -> None:
    o_v = OptionalValidator(StringValidator())
    assert o_v(None) == Valid(None)
    assert o_v(5) == Invalid(
        o_v,
        5,
        VariantErrs(
            [
                Invalid(o_v.validator.validators[0], 5, TypeErr(type(None))),
                Invalid(o_v.validator.validators[1], 5, TypeErr(str)),
            ],
        ),
    )
    assert o_v("okok") == Valid("okok")


@pytest.mark.asyncio
async def test_optional_validator_async() -> None:
    o_v = OptionalValidator(StringValidator())
    assert await o_v.validate_async(None) == Valid(None)
    assert await o_v.validate_async(5) == Invalid(
        o_v,
        5,
        VariantErrs(
            [
                Invalid(o_v.validator.validators[0], 5, TypeErr(type(None))),
                Invalid(o_v.validator.validators[1], 5, TypeErr(str)),
            ],
        ),
    )
    assert await o_v.validate_async("okok") == Valid("okok")
