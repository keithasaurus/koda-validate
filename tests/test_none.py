import pytest

from koda_validate import IntValidator, Invalid, OptionalValidator, StringValidator, Valid
from koda_validate.base import TypeErr, VariantErrs
from koda_validate.none import NoneValidator, none_validator


def test_none() -> None:
    assert none_validator("a string") == Invalid(
        TypeErr(type(None)), "a string", none_validator
    )

    assert none_validator(None) == Valid(None)

    assert none_validator(False) == Invalid(TypeErr(type(None)), False, none_validator)


def test_none_repr() -> None:
    assert repr(NoneValidator()) == repr(none_validator) == "NoneValidator()"


def test_none_eq() -> None:
    assert NoneValidator() == NoneValidator() == none_validator
    assert NoneValidator() is NoneValidator() is none_validator


@pytest.mark.asyncio
async def test_none_async() -> None:
    assert await none_validator.validate_async("a string") == Invalid(
        TypeErr(type(None)), "a string", none_validator
    )

    assert await none_validator.validate_async(None) == Valid(None)

    assert await none_validator.validate_async(False) == Invalid(
        TypeErr(type(None)), False, none_validator
    )


def test_optional_validator() -> None:
    o_v = OptionalValidator(StringValidator())
    assert o_v(None) == Valid(None)
    assert o_v(5) == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(type(None)), 5, none_validator),
                Invalid(TypeErr(str), 5, o_v.non_none_validator),
            ],
        ),
        5,
        o_v,
    )
    assert o_v("okok") == Valid("okok")


@pytest.mark.asyncio
async def test_optional_validator_async() -> None:
    o_v = OptionalValidator(StringValidator())
    assert await o_v.validate_async(None) == Valid(None)
    assert await o_v.validate_async(5) == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(type(None)), 5, none_validator),
                Invalid(TypeErr(str), 5, o_v.non_none_validator),
            ],
        ),
        5,
        o_v,
    )
    assert await o_v.validate_async("okok") == Valid("okok")


def test_optional_repr() -> None:
    assert (
        repr(OptionalValidator(StringValidator()))
        == "OptionalValidator(StringValidator())"
    )
    assert repr(OptionalValidator(IntValidator())) == "OptionalValidator(IntValidator())"


def test_optional_eq() -> None:
    assert OptionalValidator(StringValidator()) == OptionalValidator(StringValidator())

    assert OptionalValidator(IntValidator()) != OptionalValidator(StringValidator())
