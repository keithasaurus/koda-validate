import pytest
from koda import Err, First, Ok, Second, Third

from koda_validate import FloatValidator, IntValidator, OneOf2, OneOf3, StringValidator


def test_one_of2() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert str_or_int_validator("ok") == Ok(First("ok"))
    assert str_or_int_validator(5) == Ok(Second(5))
    assert str_or_int_validator(5.5) == Err(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )


@pytest.mark.asyncio
async def test_one_of2_async() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert await str_or_int_validator.validate_async("ok") == Ok(First("ok"))
    assert await str_or_int_validator.validate_async(5) == Ok(Second(5))
    assert await str_or_int_validator.validate_async(5.5) == Err(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )


def test_one_of3() -> None:
    str_or_int_or_float_validator = OneOf3(
        StringValidator(), IntValidator(), FloatValidator()
    )
    assert str_or_int_or_float_validator("ok") == Ok(First("ok"))
    assert str_or_int_or_float_validator(5) == Ok(Second(5))
    assert str_or_int_or_float_validator(5.5) == Ok(Third(5.5))
    assert str_or_int_or_float_validator(True) == Err(
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
    assert await str_or_int_or_float_validator.validate_async("ok") == Ok(First("ok"))
    assert await str_or_int_or_float_validator.validate_async(5) == Ok(Second(5))
    assert await str_or_int_or_float_validator.validate_async(5.5) == Ok(Third(5.5))
    assert await str_or_int_or_float_validator.validate_async(True) == Err(
        {
            "variant 1": ["expected a string"],
            "variant 2": ["expected an integer"],
            "variant 3": ["expected a float"],
        }
    )
