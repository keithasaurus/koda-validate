from decimal import Decimal

from koda import Err, Ok

from koda_validate import Invalid, Valid


def test_valid_repr() -> None:
    assert repr(Valid(Decimal("0.50"))) == "Valid(Decimal('0.50'))"


def test_valid_as_result() -> None:
    assert Valid(123).as_result == Ok(123)


def test_invalid_repr() -> None:
    assert repr(Invalid(Decimal("0.50"))) == "Invalid(Decimal('0.50'))"


def test_invalid_as_result() -> None:
    assert Invalid(123).as_result == Err(123)
