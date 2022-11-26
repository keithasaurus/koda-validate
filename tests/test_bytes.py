import pytest

from koda_validate import Invalid, Valid
from koda_validate.base import InvalidType
from koda_validate.bytes import BytesValidator


def test_bytes() -> None:
    assert BytesValidator()(b"okokok") == Valid(b"okokok")
    assert BytesValidator()("wrong type!") == Invalid(
        InvalidType(bytes, "expected a bytes object")
    )


@pytest.mark.asyncio
async def test_bytes_async() -> None:
    assert await BytesValidator().validate_async(b"okokok") == Valid(b"okokok")
    assert await BytesValidator().validate_async("wrong type!") == Invalid(
        InvalidType(bytes, "expected a bytes object")
    )
