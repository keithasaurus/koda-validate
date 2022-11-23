import pytest
from koda import First, Second, Third

from koda_validate import FloatValidator, IntValidator, OneOf2, OneOf3, StringValidator
from koda_validate.base import TypeErr, VariantErrs
from koda_validate.validated import Invalid, Valid


def test_one_of2() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert str_or_int_validator("ok") == Valid(First("ok"))
    assert str_or_int_validator(5) == Valid(Second(5))
    assert str_or_int_validator(5.5) == Invalid(
        VariantErrs(
            [TypeErr(str, "expected a string"), TypeErr(int, "expected an integer")]
        )
    )


@pytest.mark.asyncio
async def test_one_of2_async() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert await str_or_int_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_validator.validate_async(5.5) == Invalid(
        VariantErrs(
            [TypeErr(str, "expected a string"), TypeErr(int, "expected an integer")]
        )
    )


def test_one_of3() -> None:
    str_or_int_or_float_validator = OneOf3(
        StringValidator(), IntValidator(), FloatValidator()
    )
    assert str_or_int_or_float_validator("ok") == Valid(First("ok"))
    assert str_or_int_or_float_validator(5) == Valid(Second(5))
    assert str_or_int_or_float_validator(5.5) == Valid(Third(5.5))
    assert str_or_int_or_float_validator(True) == Invalid(
        VariantErrs(
            [
                TypeErr(str, "expected a string"),
                TypeErr(int, "expected an integer"),
                TypeErr(float, "expected a float"),
            ]
        )
    )


@pytest.mark.asyncio
async def test_one_of3_async() -> None:
    str_or_int_or_float_validator = OneOf3(
        StringValidator(), IntValidator(), FloatValidator()
    )
    assert await str_or_int_or_float_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_or_float_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_or_float_validator.validate_async(5.5) == Valid(Third(5.5))
    assert await str_or_int_or_float_validator.validate_async(True) == Invalid(
        VariantErrs(
            [
                TypeErr(str, "expected a string"),
                TypeErr(int, "expected an integer"),
                TypeErr(float, "expected a float"),
            ]
        )
    )
