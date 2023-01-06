from typing import Any

import pytest
from koda import Just, Maybe, nothing

from koda_validate import IntValidator, Invalid, StringValidator, TypeErr, Valid
from koda_validate.errors import ContainerErr
from koda_validate.maybe import MaybeValidator


def test_works_with_nothing() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert mi_v(nothing) == Valid(nothing)


def test_works_with_valid_just() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert mi_v(Just(5)) == Valid(Just(5))


def test_invalid_with_invalid_just() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert mi_v(Just("abc")) == Invalid(
        ContainerErr(
            Invalid(TypeErr(int), "abc", mi_v.validator),
        ),
        Just("abc"),
        mi_v,
    )


def test_not_maybe_is_invalid() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert mi_v("abc") == Invalid(TypeErr(Maybe[Any]), "abc", mi_v)  # type: ignore[misc]


@pytest.mark.asyncio
async def test_works_with_nothing_async() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert await mi_v.validate_async(nothing) == Valid(nothing)


@pytest.mark.asyncio
async def test_works_with_valid_just_async() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert await mi_v.validate_async(Just(5)) == Valid(Just(5))


@pytest.mark.asyncio
async def test_invalid_with_invalid_just_async() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert await mi_v.validate_async(Just("abc")) == Invalid(
        ContainerErr(
            Invalid(TypeErr(int), "abc", mi_v.validator),
        ),
        Just("abc"),
        mi_v,
    )


@pytest.mark.asyncio
async def test_not_maybe_is_invalid_async() -> None:
    mi_v = MaybeValidator(IntValidator())

    assert await mi_v.validate_async("abc") == Invalid(
        TypeErr(Maybe[Any]), "abc", mi_v  # type: ignore[misc]
    )


def test_eq() -> None:
    assert MaybeValidator(StringValidator()) == MaybeValidator(StringValidator())
    assert MaybeValidator(StringValidator()) != MaybeValidator(IntValidator())


def test_repr() -> None:
    assert repr(MaybeValidator(StringValidator())) == "MaybeValidator(StringValidator())"
