from typing import Any

import pytest
from koda import Just, Maybe, nothing

from koda_validate import (
    IntValidator,
    Invalid,
    OptionalValidator,
    StringValidator,
    TypeErr,
    UnionErrs,
    Valid,
)
from koda_validate.coerce import coercer
from koda_validate.none import NoneValidator, none_validator


def test_none() -> None:
    assert none_validator("a string") == Invalid(
        TypeErr(type(None)), "a string", none_validator
    )

    assert none_validator(None) == Valid(None)

    assert none_validator(False) == Invalid(TypeErr(type(None)), False, none_validator)


def test_none_repr() -> None:
    assert repr(NoneValidator()) == repr(none_validator) == "NoneValidator(coerce=None)"


def test_none_eq() -> None:
    @coercer(bool)
    def coerce_false_to_none(val: Any) -> Maybe[None]:
        if val is False:
            return Just(None)
        return nothing

    assert NoneValidator() == NoneValidator() == none_validator
    assert NoneValidator() != NoneValidator(coerce=coerce_false_to_none)


def test_none_coerce() -> None:
    @coercer(bool)
    def coerce_false_to_none(val: Any) -> Maybe[None]:
        if val is False:
            return Just(None)
        return nothing

    validator = NoneValidator(coerce=coerce_false_to_none)
    assert validator(False) == Valid(None)
    assert isinstance(validator(None), Invalid)


@pytest.mark.asyncio
async def test_none_coerce_async() -> None:
    @coercer(bool)
    def coerce_false_to_none(val: Any) -> Maybe[None]:
        if val is False:
            return Just(None)
        return nothing

    validator = NoneValidator(coerce=coerce_false_to_none)
    assert await validator.validate_async(False) == Valid(None)
    assert isinstance(await validator.validate_async(None), Invalid)


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
        UnionErrs(
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
        UnionErrs(
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
