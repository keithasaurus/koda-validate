import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Hashable, List, Optional, Union, cast

from koda import Maybe

from koda_validate import (
    BoolValidator,
    Choices,
    DatetimeValidator,
    DateValidator,
    DecimalValidator,
    EqualsValidator,
    FloatValidator,
    IntValidator,
    Invalid,
    IsDictValidator,
    Lazy,
    ListValidator,
    MapValidator,
    Max,
    MaxItems,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    MultipleOf,
    NoneValidator,
    OneOf2,
    OneOf3,
    OptionalValidator,
    RegexPredicate,
    StringValidator,
    Valid,
    Validator,
    none_validator,
    strip,
)
from koda_validate.base import (
    InvalidDict,
    InvalidKeyVal,
    InvalidMap,
    InvalidMissingKey,
    InvalidSimple,
    InvalidType,
    InvalidVariants,
    ValidationResult,
)
from koda_validate.dataclasses import DataclassValidator, get_typehint_validator
from koda_validate.dictionary import (
    DictValidatorAny,
    KeyNotRequired,
    MaxKeys,
    MinKeys,
    RecordValidator,
    is_dict_validator,
)
from koda_validate.generic import AlwaysValid
from koda_validate.tuple import (
    Tuple2Validator,
    Tuple3Validator,
    TupleHomogenousValidator,
    TupleNValidatorAny,
)
from koda_validate.union import UnionValidatorAny


@dataclass
class Person:
    name: str
    age: Maybe[int]


def test_match_args() -> None:
    match BoolValidator():
        case BoolValidator(predicates_bool):
            assert predicates_bool == ()
        case _:
            assert False

    match DecimalValidator():
        case DecimalValidator(predicates_decimal):
            assert predicates_decimal == ()
        case _:
            assert False

    match MapValidator(key=(str_ := StringValidator()), value=(int_ := IntValidator())):
        case MapValidator(
            string_validator, int_validator, predicates_map, preds_async_2, process_2
        ):
            assert string_validator == str_
            assert int_validator == int_
            assert predicates_map is None
            assert preds_async_2 is None
            assert process_2 is None

    match is_dict_validator:
        case IsDictValidator():
            assert True
        case _:
            assert False

    match MinKeys(5):
        case MinKeys(min_keys_size):
            assert min_keys_size == 5
        case _:
            assert False

    match MaxKeys(5):
        case MaxKeys(max_keys_size):
            assert max_keys_size == 5
        case _:
            assert False


def test_record_validator_match_args() -> None:
    def validate_person(p: Person) -> ValidationResult[Person]:
        if len(p.name) > p.age.get_or_else(100):
            return Invalid(InvalidSimple("your name cannot be longer than your age"))
        else:
            return Valid(p)

    dv_validator = RecordValidator(
        into=(into_ := Person),
        keys=(
            (str_1 := ("name", StringValidator())),
            (int_1 := ("age", KeyNotRequired(IntValidator()))),
        ),
        validate_object=validate_person,
    )
    match dv_validator:
        case RecordValidator(
            fields_dv, into, preprocessors, validate_object, validate_object_async
        ):
            assert into == into_
            assert fields_dv[0] == str_1
            assert fields_dv[1][0] == "age"
            knr = fields_dv[1][1]
            assert isinstance(knr, KeyNotRequired)
            # # mypy doesn't quite understand `KeyNotRequired`,
            # # and sees the next line as unreachable. This is because of the
            # # isinstance on the preceding line.
            assert knr.validator == int_1[1].validator
            assert validate_object == validate_person
            assert validate_object_async is None
            assert preprocessors is None

        case _:
            assert False


def test_dict_any_match_args() -> None:
    def validate_person_dict_any(p: Dict[Any, Any]) -> ValidationResult[Dict[Any, Any]]:
        if len(p["name"]) > p["age"]:
            return Invalid(InvalidSimple("your name cannot be longer than your name"))
        else:
            return Valid(p)

    schema_: Dict[Hashable, Validator[Any, Any]] = {
        "name": StringValidator(),
        "age": IntValidator(),
    }
    dva_validator = DictValidatorAny(
        schema_,
        validate_object=validate_person_dict_any,
    )
    match dva_validator:
        case DictValidatorAny(
            fields_dva, preprocessors_dva, validate_object_dva, validate_object_async_dva
        ):
            assert fields_dva is schema_
            assert validate_object_dva == validate_person_dict_any
            assert preprocessors_dva is None
            assert validate_object_async_dva is None

        case _:
            assert False


def test_float_validator_match_args() -> None:
    match FloatValidator():
        case FloatValidator(preds):
            assert preds == ()
        case _:
            assert False


def test_lazy_match_args() -> None:
    def lazy_dv_validator() -> RecordValidator[Person]:
        return dv_validator_2

    dv_validator_2: RecordValidator[Person] = RecordValidator(
        into=Person,
        keys=(
            ("name", StringValidator()),
            ("age", KeyNotRequired(IntValidator())),
        ),
    )
    match Lazy(lazy_dv_validator):
        case Lazy(validator, recurrent):
            assert validator is lazy_dv_validator
            assert recurrent is True

        case _:
            assert False


def test_generic_match() -> None:
    match Choices({1, 2, 3}):
        case Choices(choices):
            assert choices == {1, 2, 3}
        case _:
            assert False

    match Min(5):
        case Min(num, excl):
            assert num == 5
            assert excl is False
        case _:
            assert False

    match Max(5):
        case Max(num, excl):
            assert num == 5
            assert excl is False
        case _:
            assert False

    match MultipleOf(3):
        case MultipleOf(num):
            assert num == 3
        case _:
            assert False

    match EqualsValidator("abc"):
        case EqualsValidator(match, preprocessors_exact):
            assert match == "abc"
            assert preprocessors_exact is None

    match IntValidator((int_min := Min(5))):
        case IntValidator(predicates):
            assert predicates == (int_min,)
        case _:
            assert False

    match MinLength(2):
        case MinLength(length):
            assert length == 2
        case _:
            assert False

    match MaxLength(2):
        case MaxLength(length):
            assert length == 2
        case _:
            assert False

    match MinItems(2):
        case MinItems(length):
            assert length == 2
        case _:
            assert False

    match MaxItems(2):
        case MaxItems(length):
            assert length == 2
        case _:
            assert False


def test_list_validator_match() -> None:
    match ListValidator(
        (str_vldtr := StringValidator()), predicates=[min_items_ := MinItems(2)]
    ):
        case ListValidator(item_validator, preds_1, preds_async_1, preprocess_1):
            assert item_validator is str_vldtr
            assert preds_1 == [min_items_]
            assert preds_async_1 is None
            assert preprocess_1 is None


def test_optional_validator_match() -> None:
    match OptionalValidator(str_3 := StringValidator()):
        case OptionalValidator(opt_validator):
            assert isinstance(opt_validator, UnionValidatorAny)
            assert opt_validator.validators[0] is none_validator
            assert opt_validator.validators[1] is str_3

        case _:
            assert False


def test_one_of_two_match() -> None:
    match OneOf2(
        s_3 := StringValidator(),
        i_3 := IntValidator(),
    ):
        case OneOf2(var_1, var_2):
            assert var_1 is s_3
            assert var_2 is i_3
        case _:
            assert False


def test_one_of_3_match() -> None:
    match OneOf3(
        s_4 := StringValidator(), i_4 := IntValidator(), f_4 := FloatValidator()
    ):
        case OneOf3(var_1, var_2, var_3):
            assert var_1 is s_4
            assert var_2 is i_4
            assert var_3 is f_4
        case _:
            assert False


def test_string_validator_match() -> None:
    match StringValidator(preprocessors=[strip]):
        case StringValidator(preds_6, preds_async, preproc_6):
            assert preds_6 == ()
            assert preds_async is None
            assert preproc_6 == [strip]
        case _:
            assert False


def test_regex_predicate_match() -> None:
    match RegexPredicate(ptrn := re.compile("abc")):
        case RegexPredicate(pattern):
            assert pattern is ptrn
        case _:
            assert False


def test_date_string_validator() -> None:
    match DateValidator():
        case DateValidator(pred_7):
            assert pred_7 == ()
        case _:
            assert False


def test_datetime_string_validator() -> None:
    match DatetimeValidator():
        case DatetimeValidator(pred_8):
            assert pred_8 == ()
        case _:
            assert False


def test_tuple_match() -> None:
    match Tuple2Validator(
        s_8 := StringValidator(),
        i_8 := IntValidator(),
    ):
        case Tuple2Validator(vldtr_8, vldtr_9):
            assert vldtr_8 is s_8
            assert vldtr_9 is i_8

        case _:
            assert False

    match Tuple3Validator(
        s_9 := StringValidator(), i_9 := IntValidator(), f_9 := FloatValidator()
    ):
        case Tuple3Validator(vldtr_1, vldtr_2, vldtr_3):
            assert vldtr_1 is s_9
            assert vldtr_2 is i_9
            assert vldtr_3 is f_9
        case _:
            assert False


def test_always_valid_match() -> None:
    match AlwaysValid():
        case AlwaysValid():
            assert True
        case _:
            assert False


@dataclass
class PersonSimple:
    name: str
    age: int


def test_get_typehint_validator_list_union() -> None:
    for validator in [
        get_typehint_validator(list[str | int]),
        get_typehint_validator(list[Union[str, int]]),
    ]:
        assert isinstance(validator, ListValidator)
        assert isinstance(validator.item_validator, UnionValidatorAny)
        assert len(validator.item_validator.validators) == 2
        assert isinstance(validator.item_validator.validators[0], StringValidator)
        assert isinstance(validator.item_validator.validators[1], IntValidator)


# should be in test_dataclasses
def test_complex_union_dataclass() -> None:
    @dataclass
    class Example:
        a: Optional[str] | float | int

    example_validator = DataclassValidator(Example)
    assert example_validator({"a": "ok"}) == Valid(Example("ok"))
    assert example_validator({"a": None}) == Valid(Example(None))
    assert example_validator({"a": 1.1}) == Valid(Example(1.1))
    assert example_validator({"a": 5}) == Valid(Example(5))

    validators_schema_key_a = cast(UnionValidatorAny, example_validator.schema["a"])
    assert example_validator({"a": False}) == Invalid(
        InvalidDict(
            example_validator,
            {
                "a": InvalidVariants(
                    example_validator.schema["a"],
                    [
                        InvalidType(validators_schema_key_a.validators[0], str),
                        InvalidType(validators_schema_key_a.validators[1], type(None)),
                        InvalidType(validators_schema_key_a.validators[2], float),
                        InvalidType(validators_schema_key_a.validators[3], int),
                    ],
                )
            },
        )
    )


def test_nested_dataclass() -> None:
    @dataclass
    class A:
        name: str
        lottery_numbers: list[int]
        awake: bool
        something: dict[str, int]

    @dataclass
    class B:
        name: str
        rating: float
        a: A

    b_validator = DataclassValidator(B)

    assert b_validator(
        {
            "name": "bob",
            "rating": 5.5,
            "a": {
                "name": "keith",
                "awake": False,
                "lottery_numbers": [1, 2, 3],
                "something": {},
            },
        }
    ) == Valid(
        B(
            name="bob",
            rating=5.5,
            a=A(name="keith", lottery_numbers=[1, 2, 3], awake=False, something={}),
        )
    )
    assert b_validator(
        {
            "rating": 5.5,
            "a": {
                "name": "keith",
                "awake": False,
                "lottery_numbers": [1, 2, 3],
                "something": {},
            },
        }
    ) == Invalid(InvalidDict(b_validator, {"name": InvalidMissingKey(b_validator)}))

    assert b_validator(
        {
            "name": "whatever",
            "rating": 5.5,
            "a": {
                "name": "keith",
                "awake": False,
                "lottery_numbers": [1, 2, 3],
                "something": {5: 5},
            },
        }
    ) == Invalid(
        InvalidDict(
            b_validator,
            {
                "a": InvalidDict(
                    b_validator.schema["a"],
                    {
                        "something": InvalidMap(
                            b_validator.schema["a"].schema["something"],  # type: ignore
                            {
                                5: InvalidKeyVal(
                                    key=InvalidType(
                                        b_validator.schema["a"].schema["something"].key_validator,  # type: ignore  # noqa: E501
                                        str,
                                    ),
                                    val=None,
                                )
                            },
                        )
                    },
                )
            },
        )
    )


def test_get_typehint_validator() -> None:
    assert isinstance(get_typehint_validator(Any), AlwaysValid)
    assert isinstance(get_typehint_validator(None), NoneValidator)
    assert isinstance(get_typehint_validator(str), StringValidator)
    assert isinstance(get_typehint_validator(int), IntValidator)
    assert isinstance(get_typehint_validator(float), FloatValidator)
    assert isinstance(get_typehint_validator(Decimal), DecimalValidator)
    assert isinstance(get_typehint_validator(bool), BoolValidator)

    for bare_list_validator in [
        get_typehint_validator(list),
        get_typehint_validator(List),
        get_typehint_validator(list[Any]),
        get_typehint_validator(List[Any]),
    ]:
        assert isinstance(bare_list_validator, ListValidator)
        assert isinstance(bare_list_validator.item_validator, AlwaysValid)

    for bare_dict_validator in [
        get_typehint_validator(dict),
        get_typehint_validator(Dict),
        get_typehint_validator(Dict[Any, Any]),
        get_typehint_validator(dict[Any, Any]),
    ]:
        assert isinstance(bare_dict_validator, MapValidator)
        assert isinstance(bare_dict_validator.key_validator, AlwaysValid)
        assert isinstance(bare_dict_validator.value_validator, AlwaysValid)

    dataclass_validator = get_typehint_validator(PersonSimple)
    assert isinstance(dataclass_validator, DataclassValidator)
    assert dataclass_validator.data_cls is PersonSimple

    optional_str_validator = get_typehint_validator(Optional[str])
    assert isinstance(optional_str_validator, UnionValidatorAny)
    assert isinstance(optional_str_validator.validators[0], StringValidator)
    assert isinstance(optional_str_validator.validators[1], NoneValidator)

    union_str_int_validator = get_typehint_validator(Union[str, int, bool])
    assert isinstance(union_str_int_validator, UnionValidatorAny)
    assert len(union_str_int_validator.validators) == 3
    assert isinstance(union_str_int_validator.validators[0], StringValidator)
    assert isinstance(union_str_int_validator.validators[1], IntValidator)
    assert isinstance(union_str_int_validator.validators[2], BoolValidator)

    union_opt_str_int_validator = get_typehint_validator(Union[Optional[str], int, bool])
    assert isinstance(union_opt_str_int_validator, UnionValidatorAny)
    assert len(union_opt_str_int_validator.validators) == 4
    assert isinstance(union_opt_str_int_validator.validators[0], StringValidator)
    assert isinstance(union_opt_str_int_validator.validators[1], NoneValidator)
    assert isinstance(union_opt_str_int_validator.validators[2], IntValidator)
    assert isinstance(union_opt_str_int_validator.validators[3], BoolValidator)


def test_get_typehint_validator_tuple_n_any() -> None:
    t_n_any_validator = get_typehint_validator(tuple[str, int])  # type: ignore
    assert isinstance(t_n_any_validator, TupleNValidatorAny)
    assert len(t_n_any_validator.validators) == 2
    assert isinstance(t_n_any_validator.validators[0], StringValidator)
    assert isinstance(t_n_any_validator.validators[1], IntValidator)


def test_get_typehint_validator_tuple_homogenous() -> None:
    tuple_homogeneous_validator_1 = get_typehint_validator(tuple[str, ...])
    assert isinstance(tuple_homogeneous_validator_1, TupleHomogenousValidator)
    assert isinstance(tuple_homogeneous_validator_1.item_validator, StringValidator)
