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
        str_or_int_validator,
        5.5,
        VariantErrs(
            [
                Invalid(s_v, 5.5, TypeErr(str)),
                Invalid(i_v, 5.5, TypeErr(int)),
            ],
        ),
    )


@pytest.mark.asyncio
async def test_one_of2_async() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    str_or_int_validator = OneOf2(s_v, i_v)
    assert await str_or_int_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_validator.validate_async(5.5) == Invalid(
        str_or_int_validator,
        5.5,
        VariantErrs(
            [
                Invalid(s_v, 5.5, TypeErr(str)),
                Invalid(i_v, 5.5, TypeErr(int)),
            ],
        ),
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
        str_or_int_or_float_validator,
        True,
        VariantErrs(
            [
                Invalid(str_v, True, TypeErr(str)),
                Invalid(int_v, True, TypeErr(int)),
                Invalid(fl_v, True, TypeErr(float)),
            ],
        ),
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
        str_or_int_or_float_validator,
        True,
        VariantErrs(
            [
                Invalid(str_v, True, TypeErr(str)),
                Invalid(int_v, True, TypeErr(int)),
                Invalid(fl_v, True, TypeErr(float)),
            ],
        ),
    )
