from decimal import Decimal

from koda import Err, Ok

from koda_validate import Invalid, StringValidator, Valid
from koda_validate.base import InvalidType


def test_valid_repr() -> None:
    assert repr(Valid(Decimal("0.50"))) == "Valid(Decimal('0.50'))"


def test_valid_as_result() -> None:
    assert Valid(123).as_result == Ok(123)


def test_invalid_repr() -> None:
    invalid_type = InvalidType(StringValidator(), str)
    assert repr(Invalid(invalid_type)) == f"Invalid({repr(invalid_type)})"


def test_invalid_as_result() -> None:
    invalid_type = InvalidType(StringValidator(), str)
    assert Invalid(invalid_type).as_result == Err(invalid_type)
