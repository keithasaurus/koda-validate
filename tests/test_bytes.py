import pytest

from koda_validate import Invalid, Valid
from koda_validate.base import TypeErr
from koda_validate.bytes import BytesValidator


def test_bytes() -> None:
    b_v = BytesValidator()
    assert b_v(b"okokok") == Valid(b"okokok")
    assert b_v("wrong type!") == Invalid(TypeErr(bytes), "wrong type!", b_v)


@pytest.mark.asyncio
async def test_bytes_async() -> None:
    b_v = BytesValidator()
    assert await b_v.validate_async(b"okokok") == Valid(b"okokok")
    assert await b_v.validate_async("wrong type!") == Invalid(
        TypeErr(bytes), "wrong type!", b_v
    )
