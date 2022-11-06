import pytest
from koda import First, Second, Third

from koda_validate import FloatValidator, IntValidator, OneOf2, OneOf3, StringValidator
from koda_validate.typedefs import Invalid, Valid


def test_one_of2() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert str_or_int_validator("ok") == Valid(First("ok"))
    assert str_or_int_validator(5) == Valid(Second(5))
    assert str_or_int_validator(5.5) == Invalid(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )


@pytest.mark.asyncio
async def test_one_of2_async() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert await str_or_int_validator.validate_async("ok") == Valid(First("ok"))
    assert await str_or_int_validator.validate_async(5) == Valid(Second(5))
    assert await str_or_int_validator.validate_async(5.5) == Invalid(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )


def test_one_of3() -> None:
    str_or_int_or_float_validator = OneOf3(
        StringValidator(), IntValidator(), FloatValidator()
    )
    assert str_or_int_or_float_validator("ok") == Valid(First("ok"))
    assert str_or_int_or_float_validator(5) == Valid(Second(5))
    assert str_or_int_or_float_validator(5.5) == Valid(Third(5.5))
    assert str_or_int_or_float_validator(True) == Invalid(
        {
            "variant 1": ["expected a string"],
            "variant 2": ["expected an integer"],
            "variant 3": ["expected a float"],
        }
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
        {
            "variant 1": ["expected a string"],
            "variant 2": ["expected an integer"],
            "variant 3": ["expected a float"],
        }
    )
