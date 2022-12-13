from datetime import date, datetime
from decimal import Decimal
from typing import Literal, NamedTuple, Tuple

from koda_validate import (
    AlwaysValid,
    DatetimeValidator,
    DateValidator,
    EqualsValidator,
    EqualTo,
    Invalid,
    PredicateErrs,
    TupleHomogenousValidator,
    TypeErr,
    UnionValidator,
    Valid,
    VariantErrs,
)
from koda_validate.namedtuple import NamedTupleValidator
from koda_validate.typehints import get_typehint_validator


def test_get_typehint_validator_bare_tuple() -> None:
    for t_validator in [get_typehint_validator(tuple), get_typehint_validator(Tuple)]:
        assert isinstance(t_validator, TupleHomogenousValidator)
        assert isinstance(t_validator.item_validator, AlwaysValid)


def test_get_type_hint_for_literal() -> None:
    abc_validator = get_typehint_validator(Literal["abc"])
    assert isinstance(abc_validator, UnionValidator)

    assert len(abc_validator.validators) == 1
    assert isinstance(abc_validator.validators[0], EqualsValidator)
    assert abc_validator("abc") == Valid("abc")
    assert abc_validator("a") == Invalid(
        VariantErrs(
            [Invalid(PredicateErrs([EqualTo("abc")]), "a", abc_validator.validators[0])]
        ),
        "a",
        abc_validator,
    )

    int_str_bool_validator = get_typehint_validator(Literal[123, "abc", False])
    assert isinstance(int_str_bool_validator, UnionValidator)

    assert len(int_str_bool_validator.validators) == 3
    for v in int_str_bool_validator.validators:
        assert isinstance(v, EqualsValidator)

    assert int_str_bool_validator(123) == Valid(123)
    assert int_str_bool_validator("abc") == Valid("abc")
    assert int_str_bool_validator(False) == Valid(False)

    assert int_str_bool_validator("a") == Invalid(
        VariantErrs(
            [
                Invalid(TypeErr(int), "a", int_str_bool_validator.validators[0]),
                Invalid(
                    PredicateErrs([EqualTo("abc")]),
                    "a",
                    int_str_bool_validator.validators[1],
                ),
                Invalid(TypeErr(bool), "a", int_str_bool_validator.validators[2]),
            ]
        ),
        "a",
        int_str_bool_validator,
    )


def test_get_typehint_validator_named_tuple() -> None:
    class X(NamedTuple):
        x: str

    v = get_typehint_validator(X)

    assert isinstance(v, NamedTupleValidator)
    assert v == NamedTupleValidator(X)


def test_datetime_handled_properly() -> None:
    assert get_typehint_validator(datetime) == DatetimeValidator()


def test_date_handled_properly() -> None:
    assert get_typehint_validator(date) == DateValidator()


def test_unhandled_message() -> None:
    for obj in ["just a string", 1, Decimal(5)]:
        try:
            get_typehint_validator(obj)
        except TypeError as e:
            assert str(e) == f"Got unhandled annotation: {repr(obj)}."
        else:
            raise AssertionError("should have raised a TypeError")
