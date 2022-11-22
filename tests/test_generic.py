from decimal import Decimal

import pytest

from koda_validate import Choices, EqualsValidator, Max, Min, MultipleOf, strip
from koda_validate.generic import always_valid
from koda_validate.validated import Invalid, Valid


def test_exactly() -> None:
    assert EqualsValidator(5)(5) == Valid(5)
    assert EqualsValidator(5)(4) == Invalid(["expected exactly 5 (int)"])
    assert EqualsValidator("ok")("ok") == Valid("ok")
    assert EqualsValidator("ok", preprocessors=[strip])(" ok ") == Valid("ok")
    assert EqualsValidator("ok")("not ok") == Invalid(['expected exactly "ok" (str)'])
    assert EqualsValidator(Decimal("1.25"))(Decimal("1.25")) == Valid(Decimal("1.25"))
    assert EqualsValidator(Decimal("1.1"))(Decimal("5")) == Invalid(
        ["expected exactly 1.1 (Decimal)"]
    )
    assert EqualsValidator(4.4)("5.5") == Invalid(["expected exactly 4.4 (float)"])
    assert EqualsValidator(True)(True) == Valid(True)
    assert EqualsValidator(False)(False) == Valid(False)
    assert EqualsValidator(True)(False) == Invalid(["expected exactly True (bool)"])
    assert EqualsValidator(4)(4.0) == Invalid(["expected exactly 4 (int)"])


@pytest.mark.asyncio
async def test_exactly_async() -> None:
    assert await EqualsValidator(5).validate_async(5) == Valid(5)
    assert await EqualsValidator(5).validate_async(4) == Invalid(
        ["expected exactly 5 (int)"]
    )
    assert await EqualsValidator("ok").validate_async("ok") == Valid("ok")
    assert await EqualsValidator("ok", preprocessors=[strip]).validate_async(
        " ok "
    ) == Valid("ok")
    assert await EqualsValidator("ok").validate_async("not ok") == Invalid(
        ['expected exactly "ok" (str)']
    )
    assert await EqualsValidator(Decimal("1.25")).validate_async(
        Decimal("1.25")
    ) == Valid(Decimal("1.25"))
    assert await EqualsValidator(Decimal("1.1")).validate_async(Decimal("5")) == Invalid(
        ["expected exactly 1.1 (Decimal)"]
    )
    assert await EqualsValidator(4.4).validate_async("5.5") == Invalid(
        ["expected exactly 4.4 (float)"]
    )
    assert await EqualsValidator(True).validate_async(True) == Valid(True)
    assert await EqualsValidator(False).validate_async(False) == Valid(False)
    assert await EqualsValidator(True).validate_async(False) == Invalid(
        ["expected exactly True (bool)"]
    )
    assert await EqualsValidator(4).validate_async(4.0) == Invalid(
        ["expected exactly 4 (int)"]
    )


def test_choices() -> None:
    validator = Choices({"a", "bc", "def"})

    assert validator("bc") is True
    assert validator("not present") is False
    assert validator.err_message == f"expected one of ['a', 'bc', 'def']"


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) is True
    assert MultipleOf(5)(11) is False
    assert MultipleOf(2.2)(4.40) is True
    assert MultipleOf(2.2).err_message == f"expected multiple of 2.2"


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


def test_any() -> None:
    assert always_valid(5) == Valid(5)
    assert always_valid([1, 2, 3]) == Valid([1, 2, 3])
    assert always_valid(False) == Valid(False)


@pytest.mark.asyncio
async def test_any_async() -> None:
    assert always_valid(5) == Valid(5)
    assert always_valid([1, 2, 3]) == Valid([1, 2, 3])
    assert always_valid(False) == Valid(False)
