import re
from decimal import Decimal
from typing import Any, List, Tuple, Union

from koda_validate import ListValidator
from koda_validate.base import (
    BasicErr,
    CoercionErr,
    DictErr,
    ExtraKeysErr,
    Invalid,
    IterableErr,
    KeyValErrs,
    MapErr,
    MissingKeyErr,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    TypeErr,
    VariantErrs,
)
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import DictValidatorAny, MapValidator, MaxKeys, MinKeys
from koda_validate.float import FloatValidator
from koda_validate.generic import (
    Choices,
    ExactItemCount,
    Max,
    MaxItems,
    Min,
    MinItems,
    MultipleOf,
    unique_items,
)
from koda_validate.integer import IntValidator
from koda_validate.serialization import pred_to_err_message, serializable_validation_err
from koda_validate.string import (
    EmailPredicate,
    MaxLength,
    MinLength,
    RegexPredicate,
    StringValidator,
    not_blank,
)
from koda_validate.union import UnionValidatorAny


def test_type_err_users_message_in_list() -> None:
    assert serializable_validation_err(Invalid(StringValidator(), TypeErr(str))) == [
        "expected str"
    ]


def test_predicate_returns_err_in_list() -> None:
    i_v = IntValidator(Min(15), Max(10))
    assert serializable_validation_err(
        Invalid(i_v, PredicateErrs([Min(15), Max(10)]))
    ) == [
        pred_to_err_message(Min(15)),
        pred_to_err_message(Max(10)),
    ]


def test_key_missing_returns_list_str() -> None:
    assert serializable_validation_err(
        Invalid(DictValidatorAny({}), MissingKeyErr())
    ) == ["key missing"]


def test_coercion_err_uses_message() -> None:
    assert serializable_validation_err(
        Invalid(DecimalValidator(), CoercionErr({str, int, Decimal}, Decimal))
    ) == ["could not coerce to Decimal (compatible with Decimal, int, str)"]


def test_iterable_errs() -> None:
    l_v = ListValidator(StringValidator())
    assert serializable_validation_err(Invalid(l_v, IterableErr({}))) == []
    assert serializable_validation_err(
        Invalid(
            l_v,
            IterableErr(
                {
                    0: Invalid(StringValidator(), TypeErr(str)),
                    5: Invalid(
                        l_v.item_validator,
                        PredicateErrs([MaxLength(10), MinLength(2)]),
                    ),
                },
            ),
        )
    ) == [
        [0, ["expected str"]],
        [5, [pred_to_err_message(MaxLength(10)), pred_to_err_message(MinLength(2))]],
    ]


def test_invalid_dict() -> None:
    assert serializable_validation_err(
        Invalid(
            DictValidatorAny({}),
            DictErr(
                {
                    5: Invalid(FloatValidator(), TypeErr(float)),
                    "ok": Invalid(DictValidatorAny({}), MissingKeyErr()),
                },
            ),
        )
    ) == {"5": ["expected float"], "ok": ["key missing"]}


def test_invalid_custom() -> None:
    assert serializable_validation_err(Invalid(StringValidator(), BasicErr("abc"))) == [
        "abc"
    ]


def test_extra_keys() -> None:
    invalid_keys = Invalid(DictValidatorAny({}), ExtraKeysErr({"a", "b", "cde"}))
    error_detail = invalid_keys.err_type
    assert isinstance(error_detail, ExtraKeysErr)
    assert serializable_validation_err(invalid_keys) == [
        "Received unknown keys. Only expected "
        + ", ".join(sorted([repr(k) for k in error_detail.expected_keys]))
        + "."
    ]


def test_map_err() -> None:
    i_v = IntValidator()
    result = serializable_validation_err(
        Invalid(
            MapValidator(key=i_v, value=StringValidator()),
            MapErr(
                {
                    5: KeyValErrs(key=Invalid(i_v, PredicateErrs([Min(6)])), val=None),
                    6: KeyValErrs(key=None, val=Invalid(StringValidator(), TypeErr(str))),
                    "7": KeyValErrs(
                        key=Invalid(IntValidator(), TypeErr(int)),
                        val=Invalid(StringValidator(), TypeErr(str)),
                    ),
                },
            ),
        )
    )

    assert result == {
        "5": {"key": [pred_to_err_message(Min(6))]},
        "6": {"value": ["expected str"]},
        "7": {"key": ["expected int"], "value": ["expected str"]},
    }


def test_variants() -> None:
    i_v = IntValidator(Min(5))
    assert serializable_validation_err(
        Invalid(
            UnionValidatorAny(StringValidator(), i_v),
            VariantErrs(
                [
                    Invalid(StringValidator(), TypeErr(str)),
                    Invalid(i_v, PredicateErrs([Min(5)])),
                ],
            ),
        )
    ) == {"variants": [["expected str"], [pred_to_err_message(Min(5))]]}


def test_pred_to_err_message() -> None:
    pred_list: List[Tuple[Union[Predicate[Any], PredicateAsync[Any]], str]] = [
        (Choices({1, 2, 3}), f"expected one of {sorted({1, 2, 3})}"),
        (MultipleOf(3), "expected multiple of 3"),
        (MinItems(2), "minimum allowed length is 2"),
        (MaxItems(2), "maximum allowed length is 2"),
        (MaxKeys(1), "maximum allowed properties is 1"),
        (MinKeys(3), "minimum allowed properties is 3"),
        (Choices({"a", "bc", "def"}), "expected one of ['a', 'bc', 'def']"),
        (Min(5), "minimum allowed value is 5"),
        (Min(5, exclusive_minimum=True), "minimum allowed value (exclusive) is 5"),
        (Max(5), "maximum allowed value is 5"),
        (Max(5, exclusive_maximum=True), "maximum allowed value (exclusive) is 5"),
        (unique_items, "all items must be unique"),
        (ExactItemCount(4), "length must be 4"),
        (not_blank, "cannot be blank"),
        (EmailPredicate(), "expected a valid email address"),
        (MinLength(3), "minimum allowed length is 3"),
        (MaxLength(5), "maximum allowed length is 5"),
        (RegexPredicate(re.compile(r".+")), r"must match pattern .+"),
    ]
    for pred, expected_str in pred_list:
        assert pred_to_err_message(pred) == expected_str
