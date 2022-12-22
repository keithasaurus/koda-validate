import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, List, NamedTuple, Tuple, Union

from koda import Just

from koda_validate import (
    BasicErr,
    CoercionErr,
    DataclassValidator,
    DatetimeValidator,
    DateValidator,
    ExtraKeysErr,
    IndexErrs,
    Invalid,
    KeyErrs,
    ListValidator,
    MapErr,
    MaxLength,
    MinLength,
    MissingKeyErr,
    NamedTupleValidator,
    NTupleValidator,
    PredicateErrs,
    SetErrs,
    TypeErr,
    UniformTupleValidator,
    UnionErrs,
    UUIDValidator,
)
from koda_validate.base import Predicate, PredicateAsync
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import DictValidatorAny, MapValidator, MaxKeys, MinKeys
from koda_validate.errors import ContainerErr, KeyValErrs
from koda_validate.float import FloatValidator
from koda_validate.generic import (
    Choices,
    EqualTo,
    ExactItemCount,
    ExactLength,
    Max,
    MaxItems,
    Min,
    MinItems,
    MultipleOf,
    unique_items,
)
from koda_validate.integer import IntValidator
from koda_validate.maybe import MaybeValidator
from koda_validate.serialization.errors import pred_to_err_message, to_serializable_errs
from koda_validate.set import SetValidator
from koda_validate.string import (
    EmailPredicate,
    RegexPredicate,
    StringValidator,
    not_blank,
)
from koda_validate.union import UnionValidator


def test_type_err_str() -> None:
    assert to_serializable_errs(Invalid(TypeErr(str), 5, StringValidator())) == [
        "expected a string"
    ]


def test_type_err_dict() -> None:
    assert to_serializable_errs(Invalid(TypeErr(dict), 5, DictValidatorAny({}))) == [
        "expected an object"
    ]


def test_type_err_list() -> None:
    assert to_serializable_errs(
        Invalid(TypeErr(list), 5, ListValidator(StringValidator()))
    ) == ["expected an array"]


def test_type_err_tuple() -> None:
    assert to_serializable_errs(
        Invalid(TypeErr(tuple), 5, UniformTupleValidator(StringValidator()))
    ) == ["expected an array"]


def test_predicate_returns_err_in_list() -> None:
    i_v = IntValidator(Min(15), Max(10))
    assert to_serializable_errs(Invalid(PredicateErrs([Min(15), Max(10)]), 12, i_v)) == [
        pred_to_err_message(Min(15)),
        pred_to_err_message(Max(10)),
    ]


def test_key_missing_returns_list_str() -> None:
    assert to_serializable_errs(Invalid(MissingKeyErr(), {}, DictValidatorAny({}))) == [
        "key missing"
    ]


def test_coercion_err_uses_message() -> None:
    assert to_serializable_errs(
        Invalid(CoercionErr({str, int, Decimal}, Decimal), "abc", DecimalValidator())
    ) == ["expected a decimal-formatted string"]


def test_iterable_errs() -> None:
    l_v = ListValidator(StringValidator())
    # shouldn't really happen, but cover it anyway...
    assert to_serializable_errs(Invalid(IndexErrs({}), [], l_v)) == []

    assert to_serializable_errs(
        Invalid(
            IndexErrs(
                {
                    0: Invalid(TypeErr(str), 1, l_v.item_validator),
                    5: Invalid(
                        PredicateErrs([MaxLength(10), MinLength(2)]),
                        "",
                        l_v.item_validator,
                    ),
                },
            ),
            [1, "", "", "", "", ""],
            l_v,
        )
    ) == [
        [0, ["expected a string"]],
        [5, [pred_to_err_message(MaxLength(10)), pred_to_err_message(MinLength(2))]],
    ]


def test_invalid_dict() -> None:
    assert to_serializable_errs(
        Invalid(
            KeyErrs(
                {
                    5: Invalid(
                        TypeErr(float),
                        "ok",
                        FloatValidator(),
                    ),
                    "ok": Invalid(
                        MissingKeyErr(),
                        {5: "ok"},
                        DictValidatorAny({}),
                    ),
                },
            ),
            {5: "ok"},
            DictValidatorAny({}),
        )
    ) == {"5": ["expected a float"], "ok": ["key missing"]}


def test_invalid_custom() -> None:
    assert to_serializable_errs(Invalid(BasicErr("abc"), "123", StringValidator())) == [
        "abc"
    ]


def test_extra_keys() -> None:
    invalid_keys = Invalid(ExtraKeysErr({"a", "b", "cde"}), {}, DictValidatorAny({}))
    error_detail = invalid_keys.err_type
    assert isinstance(error_detail, ExtraKeysErr)
    assert to_serializable_errs(invalid_keys) == {
        "__unknown_keys__": "only expected "
        + ", ".join(sorted([repr(k) for k in error_detail.expected_keys]))
    }


def test_map_err() -> None:
    i_v = IntValidator()
    result = to_serializable_errs(
        Invalid(
            MapErr(
                {
                    5: KeyValErrs(
                        key=Invalid(
                            PredicateErrs([Min(6)]),
                            5,
                            i_v,
                        ),
                        val=None,
                    ),
                    6: KeyValErrs(
                        key=None, val=Invalid(TypeErr(str), 4, StringValidator())
                    ),
                    "7": KeyValErrs(
                        key=Invalid(TypeErr(int), "7", IntValidator()),
                        val=Invalid(TypeErr(str), 4, StringValidator()),
                    ),
                },
            ),
            {5: "neat", 6: 4, "7": 4},
            MapValidator(key=i_v, value=StringValidator()),
        )
    )

    assert result == {
        "5": {"key": [pred_to_err_message(Min(6))]},
        "6": {"value": ["expected a string"]},
        "7": {"key": ["expected an integer"], "value": ["expected a string"]},
    }


def test_variants() -> None:
    i_v = IntValidator(Min(5))
    assert to_serializable_errs(
        Invalid(
            UnionErrs(
                [
                    Invalid(TypeErr(str), 5, StringValidator()),
                    Invalid(PredicateErrs([Min(5)]), 5, i_v),
                ],
            ),
            5,
            UnionValidator(StringValidator(), i_v),
        )
    ) == {"variants": [["expected a string"], [pred_to_err_message(Min(5))]]}


def test_container_err() -> None:
    assert to_serializable_errs(
        Invalid(
            ContainerErr(Invalid(TypeErr(str), 4, StringValidator())),
            Just(4),
            MaybeValidator(StringValidator()),
        )
    ) == ["expected a string"]


def test_set_errs_message() -> None:
    str_v = StringValidator()
    bad_type_err = Invalid(TypeErr(str), 1, str_v)
    bad_type_err_1 = Invalid(TypeErr(str), 2, str_v)
    assert to_serializable_errs(
        Invalid(SetErrs([bad_type_err, bad_type_err_1]), {1, 2}, SetValidator(str_v))
    ) == {
        "member_errors": [
            to_serializable_errs(bad_type_err),
            to_serializable_errs(bad_type_err_1),
        ]
    }


def test_pred_to_err_message() -> None:
    pred_list: List[Tuple[Union[Predicate[Any], PredicateAsync[Any]], str]] = [
        (Choices({1, 2, 3}), f"expected one of {sorted({1, 2, 3})}"),
        (MultipleOf(3), "expected multiple of 3"),
        (MinItems(2), "minimum allowed length is 2"),
        (MaxItems(2), "maximum allowed length is 2"),
        (MaxKeys(1), "maximum allowed properties is 1"),
        (MinKeys(3), "minimum allowed properties is 3"),
        (Choices({"a", "bc", "def"}), "expected one of ['a', 'bc', 'def']"),
        (EqualTo(5), "must equal 5"),
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
        (ExactLength(5), "expected length of 5"),
        (RegexPredicate(re.compile(r".+")), r"must match pattern .+"),
    ]
    for pred, expected_str in pred_list:
        assert pred_to_err_message(pred) == expected_str


def test_raises_err_for_unknown_pred() -> None:
    class NewPred(Predicate[str]):
        def __call__(self, val: str) -> bool:
            return val == "some str"

    np = NewPred()
    try:
        pred_to_err_message(np)
    except TypeError as e:
        assert (
            str(e)
            == f"Unhandled predicate type: {repr(type(np))}. You may want to write a "
            "wrapper function which handles that type."
        )
    else:
        assert False


def test_uuid_coercion_err() -> None:
    result = UUIDValidator()(5)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected a UUID"]


def test_decimal_coercion_err() -> None:
    result = DecimalValidator()(4.3)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected a decimal-formatted string"]


def test_datetime_coercion_err() -> None:
    result = DatetimeValidator()(4)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected an iso8601 datetime string"]


def test_date_coercion_err() -> None:
    result = DateValidator()(4)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected YYYY-MM-DD"]


def test_ntuple_coercion_err() -> None:
    result = NTupleValidator.typed(fields=(StringValidator(), IntValidator()))(4)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected an array"]


def test_dataclass_coercion_err() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    validator = DataclassValidator(Person)
    result = validator(4)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected an object"]


def test_namedtuple_coercion_err() -> None:
    class Person(NamedTuple):
        name: str
        age: int

    validator = NamedTupleValidator(Person)
    result = validator(4)
    assert isinstance(result, Invalid)
    assert to_serializable_errs(result) == ["expected an object"]


def test_default_coercion_err() -> None:
    # just pretend data
    invalid = Invalid(CoercionErr({int, float}, int), "s", IntValidator())
    assert isinstance(invalid, Invalid)
    assert to_serializable_errs(invalid) == [
        "could not coerce to int (compatible with float, int)"
    ]
