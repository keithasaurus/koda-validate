from koda_validate import FloatValidator, IntValidator, Max, Min
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
    invalid_missing_key,
)
from koda_validate.serialization import serializable_validation_err
from koda_validate.string import MaxLength, MinLength, StringValidator


def test_type_err_users_message_in_list() -> None:
    assert serializable_validation_err(InvalidType(str, StringValidator())) == [
        "expected str"
    ]


def test_predicate_returns_err_in_list() -> None:
    assert serializable_validation_err([Min(5), Max(10)]) == [
        Min(5).err_message,
        Max(10).err_message,
    ]


def test_key_missing_returns_list_str() -> None:
    assert serializable_validation_err(invalid_missing_key) == ["key missing"]


def test_coercion_err_uses_message() -> None:
    assert serializable_validation_err(
        InvalidCoercion([str, int], int, "should be str or int")
    ) == ["should be str or int"]


def test_iterable_errs() -> None:
    assert serializable_validation_err(InvalidIterable({})) == []
    assert serializable_validation_err(
        InvalidIterable(
            {0: InvalidType(str, StringValidator()), 5: [MaxLength(10), MinLength(2)]}
        )
    ) == [
        [0, ["expected str"]],
        [5, [MaxLength(10).err_message, MinLength(2).err_message]],
    ]


def test_invalid_dict() -> None:
    assert serializable_validation_err(
        InvalidDict({5: InvalidType(float, FloatValidator()), "ok": invalid_missing_key})
    ) == {"5": ["expected float"], "ok": ["key missing"]}


def test_invalid_custom() -> None:
    assert serializable_validation_err(InvalidCustom("abc")) == ["abc"]


def test_extra_keys() -> None:
    invalid_keys = InvalidExtraKeys({"a", "b", "cde"})
    assert serializable_validation_err(invalid_keys) == [invalid_keys.err_message]


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
        "5": {"key": [Min(6).err_message]},
        "6": {"value": ["expected str"]},
        "7": {"key": ["expected int"], "value": ["expected str"]},
    }


def test_variants() -> None:
    assert serializable_validation_err(
        InvalidVariants([InvalidType(str, StringValidator()), [Min(5)]])
    ) == {"variants": [["expected str"], [Min(5).err_message]]}
