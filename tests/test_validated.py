from decimal import Decimal

from koda_validate import Invalid, StringValidator, Valid
from koda_validate.base import TypeErr


def test_valid_repr() -> None:
    assert repr(Valid(Decimal("0.50"))) == "Valid(Decimal('0.50'))"


def test_invalid_repr() -> None:
    str_validator = StringValidator()
    invalid_type = TypeErr(str)
    assert (
        repr(Invalid(str_validator, invalid_type))
        == f"Invalid(validator={repr(str_validator)}, error_detail={repr(invalid_type)})"
    )
