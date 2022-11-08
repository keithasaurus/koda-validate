from decimal import Decimal
from typing import Any

from koda import Err, Ok

from koda_validate import Invalid, Valid


def test_valid_repr() -> None:
    assert repr(Valid(Decimal("0.50"))) == "Valid(Decimal('0.50'))"


def test_valid_flat_map_err() -> None:
    def fn(_: Any) -> Any:
        return Valid(5)

    assert Valid("abc").flat_map_err(fn) == Valid("abc")


def test_valid_map_err() -> None:
    def fn(_: Any) -> Any:
        return 5

    assert Valid("abc").map_err(fn) == Valid("abc")


def test_valid_as_result() -> None:
    assert Valid(123).as_result == Ok(123)


def test_invalid_repr() -> None:
    assert repr(Invalid(Decimal("0.50"))) == "Invalid(Decimal('0.50'))"


def test_invalid_flat_map() -> None:
    def fn(_: Any) -> Any:
        return Valid(5)

    assert Invalid("abc").flat_map(fn) == Invalid("abc")


def test_invalid_flat_map_err() -> None:
    def fn(_: Any) -> Any:
        return Valid(5)

    assert Invalid("abc").flat_map_err(fn) == Valid(5)


def test_valid_map() -> None:
    def fn(_: Any) -> Any:
        return 5

    assert Invalid("abc").map(fn) == Invalid("abc")


def test_invalid_as_result() -> None:
    assert Invalid(123).as_result == Err(123)
