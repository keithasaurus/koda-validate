import pytest
from koda import First, Second, Third

from koda_validate import (
    FloatValidator,
    IntValidator,
    Invalid,
    OneOf2,
    OneOf3,
    StringValidator,
    Valid,
)
from koda_validate.base import TypeErr, VariantErrs


def test_one_of2() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    str_or_int_validator = OneOf2(s_v, i_v)
    assert str_or_int_validator("ok") == Valid(First("ok"))
    assert str_or_int_validator(5) == Valid(Second(5))
    assert str_or_int_validator(5.5) == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(str), 5.5, s_v),
                Invalid(TypeErr(int), 5.5, i_v),
            ],
        ),
        5.5,
        str_or_int_validator,
    )


@pytest.mark.asyncio
async def test_one_of2_async() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    str_or_int_validator = OneOf2(s_v, i_v)
    assert await str_or_int_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_validator.validate_async(5.5) == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(str), 5.5, s_v),
                Invalid(TypeErr(int), 5.5, i_v),
            ],
        ),
        5.5,
        str_or_int_validator,
    )


def test_one_of3() -> None:
    str_v = StringValidator()
    int_v = IntValidator()
    fl_v = FloatValidator()
    str_or_int_or_float_validator = OneOf3(str_v, int_v, fl_v)
    assert str_or_int_or_float_validator("ok") == Valid(First("ok"))
    assert str_or_int_or_float_validator(5) == Valid(Second(5))
    assert str_or_int_or_float_validator(5.5) == Valid(Third(5.5))
    assert str_or_int_or_float_validator(True) == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(str), True, str_v),
                Invalid(TypeErr(int), True, int_v),
                Invalid(TypeErr(float), True, fl_v),
            ],
        ),
        True,
        str_or_int_or_float_validator,
    )


@pytest.mark.asyncio
async def test_one_of3_async() -> None:
    str_v = StringValidator()
    int_v = IntValidator()
    fl_v = FloatValidator()
    str_or_int_or_float_validator = OneOf3(str_v, int_v, fl_v)
    assert await str_or_int_or_float_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_or_float_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_or_float_validator.validate_async(5.5) == Valid(Third(5.5))
    assert await str_or_int_or_float_validator.validate_async(True) == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(str), True, str_v),
                Invalid(TypeErr(int), True, int_v),
                Invalid(TypeErr(float), True, fl_v),
            ],
        ),
        True,
        str_or_int_or_float_validator,
    )


def test_one_of_2_repr() -> None:
    assert (
        repr(OneOf2(StringValidator(), IntValidator()))
        == "OneOf2(StringValidator(), IntValidator())"
    )


def test_one_of_3_repr() -> None:
    assert (
        repr(OneOf3(StringValidator(), IntValidator(), FloatValidator()))
        == "OneOf3(StringValidator(), IntValidator(), FloatValidator())"
    )


def test_one_of_2_eq() -> None:
    str_v = StringValidator()
    int_v = IntValidator()
    assert OneOf2(str_v, int_v) == OneOf2(str_v, int_v)
    assert OneOf2(str_v, str_v) != OneOf2(str_v, int_v)


def test_one_of_3_eq() -> None:
    str_v = StringValidator()
    int_v = IntValidator()
    float_v = FloatValidator()
    assert OneOf3(str_v, int_v, float_v) == OneOf3(str_v, int_v, float_v)
    assert OneOf3(str_v, str_v, str_v) != OneOf3(str_v, int_v, float_v)
