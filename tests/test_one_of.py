import pytest
from koda import First, Second, Third

from koda_validate import FloatValidator, IntValidator, OneOf2, OneOf3, StringValidator
from koda_validate.base import InvalidType, InvalidVariants
from koda_validate.validated import Invalid, Valid


def test_one_of2() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    str_or_int_validator = OneOf2(s_v, i_v)
    assert str_or_int_validator("ok") == Valid(First("ok"))
    assert str_or_int_validator(5) == Valid(Second(5))
    assert str_or_int_validator(5.5) == Invalid(
        InvalidVariants(
            [
                InvalidType(s_v, str),
                InvalidType(i_v, int),
            ]
        )
    )


@pytest.mark.asyncio
async def test_one_of2_async() -> None:
    s_v = StringValidator()
    i_v = IntValidator()
    str_or_int_validator = OneOf2(s_v, i_v)
    assert await str_or_int_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_validator.validate_async(5.5) == Invalid(
        InvalidVariants(
            [
                InvalidType(s_v, str),
                InvalidType(i_v, int),
            ]
        )
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
        InvalidVariants(
            [
                InvalidType(str_v, str),
                InvalidType(int_v, int),
                InvalidType(fl_v, float),
            ]
        )
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
        InvalidVariants(
            [
                InvalidType(str_v, str),
                InvalidType(int_v, int),
                InvalidType(fl_v, float),
            ]
        )
    )
