from decimal import Decimal

from koda import Err, Ok

from koda_validate import DecimalValidator, Max, Min


def test_decimal() -> None:
    assert DecimalValidator()("a string") == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert DecimalValidator()(5.5) == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert DecimalValidator()(Decimal("5.5")) == Ok(Decimal("5.5"))

    assert DecimalValidator()(5) == Ok(Decimal(5))

    assert DecimalValidator(Min(Decimal(4)), Max(Decimal("5.5")))(5) == Ok(Decimal(5))
