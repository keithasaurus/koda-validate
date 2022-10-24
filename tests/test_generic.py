from decimal import Decimal

from koda import Err, Ok

from koda_validate import Choices, ExactValidator, Max, Min, MultipleOf


def test_exactly() -> None:
    assert ExactValidator(5)(5) == Ok(5)
    assert ExactValidator(5)(4) == Err(["expected exactly 5 (int)"])
    assert ExactValidator("ok")("ok") == Ok("ok")
    assert ExactValidator("ok")("not ok") == Err(['expected exactly "ok" (str)'])
    assert ExactValidator(Decimal("1.25"))(Decimal("1.25")) == Ok(Decimal("1.25"))
    assert ExactValidator(Decimal("1.1"))(Decimal("5")) == Err(
        ["expected exactly 1.1 (Decimal)"]
    )
    assert ExactValidator(4.4)("5.5") == Err(["expected exactly 4.4 (float)"])
    assert ExactValidator(True)(True) == Ok(True)
    assert ExactValidator(False)(False) == Ok(False)
    assert ExactValidator(True)(False) == Err(["expected exactly True (bool)"])
    assert ExactValidator(4)(4.0) == Err(["expected exactly 4 (int)"])


def test_choices() -> None:
    validator = Choices({"a", "bc", "def"})

    assert validator("bc") == Ok("bc")
    assert validator("not present") == Err("expected one of ['a', 'bc', 'def']")


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) == Ok(10)
    assert MultipleOf(5)(11) == Err("expected multiple of 5")
    assert MultipleOf(2.2)(4.40) == Ok(4.40)


def test_min() -> None:
    assert Min(5)(5) == Ok(5)
    assert Min(5)(4) == Err("minimum allowed value is 5")
    assert Min(5, exclusive_minimum=True)(6) == Ok(6)
    assert Min(5, exclusive_minimum=True)(5) == Err(
        "minimum allowed value (exclusive) is 5"
    )


def test_max() -> None:
    assert Max(5)(5) == Ok(5)
    assert Max(4, exclusive_maximum=True)(3) == Ok(3)
    assert Max(5)(6) == Err("maximum allowed value is 5")
    assert Max(5, exclusive_maximum=True)(5) == Err(
        "maximum allowed value (exclusive) is 5"
    )
