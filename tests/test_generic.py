from decimal import Decimal

import pytest

from koda_validate import Choices, EqualsValidator, Max, Min, MultipleOf, strip
from koda_validate.base import InvalidType
from koda_validate.generic import EqualTo, always_valid
from koda_validate.validated import Invalid, Valid


def test_equals_validator() -> None:
    assert EqualsValidator(5)(5) == Valid(5)
    assert EqualsValidator(5)(4) == Invalid([EqualTo(5)])
    assert EqualsValidator("ok")("ok") == Valid("ok")
    assert EqualsValidator("ok", preprocessors=[strip])(" ok ") == Valid("ok")
    assert EqualsValidator("ok")("not ok") == Invalid([EqualTo("ok")])
    assert EqualsValidator(Decimal("1.25"))(Decimal("1.25")) == Valid(Decimal("1.25"))
    assert EqualsValidator(Decimal("1.1"))(Decimal("5")) == Invalid(
        [EqualTo(Decimal("1.1"))]
    )
    assert EqualsValidator(4.4)("5.5") == Invalid(InvalidType(float, "expected a float"))
    assert EqualsValidator(True)(True) == Valid(True)
    assert EqualsValidator(False)(False) == Valid(False)
    assert EqualsValidator(True)(False) == Invalid([EqualTo(True)])
    assert EqualsValidator(4)(4.0) == Invalid(InvalidType(int, "expected a int"))


@pytest.mark.asyncio
async def test_equals_validator_async() -> None:
    assert await EqualsValidator(5).validate_async(5) == Valid(5)
    assert await EqualsValidator(5).validate_async(4) == Invalid([EqualTo(5)])
    assert await EqualsValidator("ok").validate_async("ok") == Valid("ok")
    assert await EqualsValidator("ok", preprocessors=[strip]).validate_async(
        " ok "
    ) == Valid("ok")
    assert await EqualsValidator("ok").validate_async("not ok") == Invalid(
        [EqualTo("ok")]
    )
    assert await EqualsValidator(Decimal("1.25")).validate_async(
        Decimal("1.25")
    ) == Valid(Decimal("1.25"))
    assert await EqualsValidator(Decimal("1.1")).validate_async(Decimal("5")) == Invalid(
        [EqualTo(Decimal("1.1"))]
    )
    assert await EqualsValidator(4.4).validate_async("5.5") == Invalid(
        InvalidType(float, "expected a float")
    )
    assert await EqualsValidator(True).validate_async(True) == Valid(True)
    assert await EqualsValidator(False).validate_async(False) == Valid(False)
    assert await EqualsValidator(True).validate_async(False) == Invalid([EqualTo(True)])
    assert await EqualsValidator(4).validate_async(4.0) == Invalid(
        InvalidType(int, "expected a int")
    )


def test_choices() -> None:
    validator = Choices({"a", "bc", "def"})

    assert validator("bc") is True
    assert validator("not present") is False
    assert validator.err_message == "expected one of ['a', 'bc', 'def']"


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) is True
    assert MultipleOf(5)(11) is False
    assert MultipleOf(2.2)(4.40) is True
    assert MultipleOf(2.2).err_message == "expected multiple of 2.2"


def test_min() -> None:
    assert Min(5)(5) is True
    assert Min(5).err_message == "minimum allowed value is 5"
    assert Min(5)(4) is False
    assert Min(5, exclusive_minimum=True)(6) is True
    assert Min(5, exclusive_minimum=True)(5) is False
    assert (
        Min(5, exclusive_minimum=True).err_message
        == "minimum allowed value (exclusive) is 5"
    )


def test_max() -> None:
    assert Max(5)(5) is True
    assert Max(4, exclusive_maximum=True)(3) is True
    assert Max(5)(6) is False
    assert Max(5).err_message == "maximum allowed value is 5"
    assert Max(5, exclusive_maximum=True)(5) is False
    assert (
        Max(5, exclusive_maximum=True).err_message
        == "maximum allowed value (exclusive) is 5"
    )


def test_always_valid() -> None:
    assert always_valid(5) == Valid(5)
    assert always_valid([1, 2, 3]) == Valid([1, 2, 3])
    assert always_valid(False) == Valid(False)


@pytest.mark.asyncio
async def test_always_valid_async() -> None:
    assert always_valid(5) == Valid(5)
    assert always_valid([1, 2, 3]) == Valid([1, 2, 3])
    assert always_valid(False) == Valid(False)
