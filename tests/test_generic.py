from decimal import Decimal

import pytest

from koda_validate import Choices, ExactValidator, Max, Min, MultipleOf, strip
from koda_validate.generic import always_valid
from koda_validate.validated import Invalid, Valid


def test_exactly() -> None:
    assert ExactValidator(5)(5) == Valid(5)
    assert ExactValidator(5)(4) == Invalid(["expected exactly 5 (int)"])
    assert ExactValidator("ok")("ok") == Valid("ok")
    assert ExactValidator("ok", preprocessors=[strip])(" ok ") == Valid("ok")
    assert ExactValidator("ok")("not ok") == Invalid(['expected exactly "ok" (str)'])
    assert ExactValidator(Decimal("1.25"))(Decimal("1.25")) == Valid(Decimal("1.25"))
    assert ExactValidator(Decimal("1.1"))(Decimal("5")) == Invalid(
        ["expected exactly 1.1 (Decimal)"]
    )
    assert ExactValidator(4.4)("5.5") == Invalid(["expected exactly 4.4 (float)"])
    assert ExactValidator(True)(True) == Valid(True)
    assert ExactValidator(False)(False) == Valid(False)
    assert ExactValidator(True)(False) == Invalid(["expected exactly True (bool)"])
    assert ExactValidator(4)(4.0) == Invalid(["expected exactly 4 (int)"])


@pytest.mark.asyncio
async def test_exactly_async() -> None:
    assert await ExactValidator(5).validate_async(5) == Valid(5)
    assert await ExactValidator(5).validate_async(4) == Invalid(
        ["expected exactly 5 (int)"]
    )
    assert await ExactValidator("ok").validate_async("ok") == Valid("ok")
    assert await ExactValidator("ok", preprocessors=[strip]).validate_async(
        " ok "
    ) == Valid("ok")
    assert await ExactValidator("ok").validate_async("not ok") == Invalid(
        ['expected exactly "ok" (str)']
    )
    assert await ExactValidator(Decimal("1.25")).validate_async(Decimal("1.25")) == Valid(
        Decimal("1.25")
    )
    assert await ExactValidator(Decimal("1.1")).validate_async(Decimal("5")) == Invalid(
        ["expected exactly 1.1 (Decimal)"]
    )
    assert await ExactValidator(4.4).validate_async("5.5") == Invalid(
        ["expected exactly 4.4 (float)"]
    )
    assert await ExactValidator(True).validate_async(True) == Valid(True)
    assert await ExactValidator(False).validate_async(False) == Valid(False)
    assert await ExactValidator(True).validate_async(False) == Invalid(
        ["expected exactly True (bool)"]
    )
    assert await ExactValidator(4).validate_async(4.0) == Invalid(
        ["expected exactly 4 (int)"]
    )


def test_choices() -> None:
    validator = Choices({"a", "bc", "def"})

    assert validator("bc") == Valid("bc")
    assert validator("not present") == Invalid("expected one of ['a', 'bc', 'def']")


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) == Valid(10)
    assert MultipleOf(5)(11) == Invalid("expected multiple of 5")
    assert MultipleOf(2.2)(4.40) == Valid(4.40)


def test_min() -> None:
    assert Min(5)(5) == Valid(5)
    assert Min(5)(4) == Invalid("minimum allowed value is 5")
    assert Min(5, exclusive_minimum=True)(6) == Valid(6)
    assert Min(5, exclusive_minimum=True)(5) == Invalid(
        "minimum allowed value (exclusive) is 5"
    )


def test_max() -> None:
    assert Max(5)(5) == Valid(5)
    assert Max(4, exclusive_maximum=True)(3) == Valid(3)
    assert Max(5)(6) == Invalid("maximum allowed value is 5")
    assert Max(5, exclusive_maximum=True)(5) == Invalid(
        "maximum allowed value (exclusive) is 5"
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
