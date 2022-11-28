import re
from decimal import Decimal
from typing import Any, List, Tuple, Union

from koda_validate.base import (
    InvalidCoercion,
    InvalidCustom,
    InvalidDict,
    InvalidExtraKeys,
    InvalidIterable,
    InvalidKeyVal,
    InvalidMap,
    InvalidType,
    InvalidVariants,
    Predicate,
    PredicateAsync,
    invalid_missing_key,
)
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import MaxKeys, MinKeys
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


def test_type_err_users_message_in_list() -> None:
    assert serializable_validation_err(InvalidType(str, StringValidator())) == [
        "expected str"
    ]


def test_predicate_returns_err_in_list() -> None:
    assert serializable_validation_err([Min(5), Max(10)]) == [
        pred_to_err_message(Min(5)),
        pred_to_err_message(Max(10)),
    ]


def test_key_missing_returns_list_str() -> None:
    assert serializable_validation_err(invalid_missing_key) == ["key missing"]


def test_coercion_err_uses_message() -> None:
    assert serializable_validation_err(
        InvalidCoercion(DecimalValidator(), [str, int, Decimal], Decimal)
    ) == ["could not coerce to Decimal (compatible with str, int, Decimal)"]


def test_iterable_errs() -> None:
    assert serializable_validation_err(InvalidIterable({})) == []
    assert serializable_validation_err(
        InvalidIterable(
            {0: InvalidType(str, StringValidator()), 5: [MaxLength(10), MinLength(2)]}
        )
    ) == [
        [0, ["expected str"]],
        [5, [pred_to_err_message(MaxLength(10)), pred_to_err_message(MinLength(2))]],
    ]


def test_invalid_dict() -> None:
    assert serializable_validation_err(
        InvalidDict({5: InvalidType(float, FloatValidator()), "ok": invalid_missing_key})
    ) == {"5": ["expected float"], "ok": ["key missing"]}


def test_invalid_custom() -> None:
    assert serializable_validation_err(InvalidCustom("abc")) == ["abc"]


def test_extra_keys() -> None:
    invalid_keys = InvalidExtraKeys({"a", "b", "cde"})
    assert serializable_validation_err(invalid_keys) == [
        "Received unknown keys. Only expected "
        + ", ".join(sorted([repr(k) for k in invalid_keys.expected_keys]))
        + "."
    ]


def test_map_err() -> None:
    result = serializable_validation_err(
        InvalidMap(
            {
                5: InvalidKeyVal(key=[Min(6)], val=None),
                6: InvalidKeyVal(key=None, val=InvalidType(str, StringValidator())),
                "7": InvalidKeyVal(
                    key=InvalidType(int, IntValidator()),
                    val=InvalidType(str, StringValidator()),
                ),
            }
        )
    )

    assert result == {
        "5": {"key": [pred_to_err_message(Min(6))]},
        "6": {"value": ["expected str"]},
        "7": {"key": ["expected int"], "value": ["expected str"]},
    }


def test_variants() -> None:
    assert serializable_validation_err(
        InvalidVariants([InvalidType(str, StringValidator()), [Min(5)]])
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
