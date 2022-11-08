import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Hashable

from koda import Maybe

from koda_validate import (
    BoolValidator,
    Choices,
    DateStringValidator,
    DatetimeStringValidator,
    DecimalValidator,
    ExactValidator,
    FloatValidator,
    IntValidator,
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
    OneOf2,
    OneOf3,
    OptionalValidator,
    RegexPredicate,
    Serializable,
    StringValidator,
    strip,
)
from koda_validate.dictionary import (
    DictValidatorAny,
    KeyNotRequired,
    MaxKeys,
    MinKeys,
    RecordValidator,
    is_dict_validator,
)
from koda_validate.generic import AlwaysValid
from koda_validate.tuple import Tuple2Validator, Tuple3Validator
from koda_validate.validated import Invalid, Valid, Validated


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
    def validate_person(p: Person) -> Validated[Person, Serializable]:
        if len(p.name) > p.age.get_or_else(100):
            return Invalid(["your name cannot be longer than your age"])
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
            # mypy doesn't quite understand `KeyNotRequired`,
            # and sees the next line as unreachable. This is because of the
            # isinstance on the preceding line.
            assert knr.validator == int_1[1].validator  # type: ignore
            assert validate_object == validate_person
            assert validate_object_async is None
            assert preprocessors is None

        case _:
            assert False


def test_dict_any_match_args() -> None:
    def validate_person_dict_any(
        p: Dict[Hashable, Any]
    ) -> Validated[Dict[Hashable, Any], Serializable]:
        if len(p["name"]) > p["age"]:
            return Invalid(["your name cannot be longer than your name"])
        else:
            return Valid(p)

    dva_validator = DictValidatorAny(
        keys=((str_0 := ("name", StringValidator())), (int_0 := ("age", IntValidator()))),
        validate_object=validate_person_dict_any,
    )
    match dva_validator:
        case DictValidatorAny(
            fields_dva, preprocessors_dva, validate_object_dva, validate_object_async_dva
        ):
            assert fields_dva[0] is str_0
            assert fields_dva[1] == int_0
            assert validate_object_dva == validate_person_dict_any
            assert preprocessors_dva is None
            assert validate_object_async_dva is None

        case _:
            assert False

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

    match ExactValidator("abc"):
        case ExactValidator(match, preprocessors_exact):
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

    match ListValidator(
        (str_vldtr := StringValidator()), predicates=[min_items_ := MinItems(2)]
    ):
        case ListValidator(item_validator, preds_1, preds_async_1, preprocess_1):
            assert item_validator is str_vldtr
            assert preds_1 == [min_items_]
            assert preds_async_1 is None
            assert preprocess_1 is None

    match OptionalValidator(str_3 := StringValidator()):
        case OptionalValidator(opt_validator):
            assert opt_validator is str_3

        case _:
            assert False

    match OneOf2(
        s_3 := StringValidator(),
        i_3 := IntValidator(),
    ):
        case OneOf2(var_1, var_2):
            assert var_1 is s_3
            assert var_2 is i_3
        case _:
            assert False

    match OneOf3(
        s_4 := StringValidator(), i_4 := IntValidator(), f_4 := FloatValidator()
    ):
        case OneOf3(var_1, var_2, var_3):
            assert var_1 is s_4
            assert var_2 is i_4
            assert var_3 is f_4
        case _:
            assert False

    match StringValidator(preprocessors=[strip]):
        case StringValidator(preds_6, preds_async, preproc_6):
            assert preds_6 == ()
            assert preds_async is None
            assert preproc_6 == [strip]
        case _:
            assert False

    match RegexPredicate(ptrn := re.compile("abc")):
        case RegexPredicate(pattern):
            assert pattern is ptrn
        case _:
            assert False

    match DateStringValidator():
        case DateStringValidator(pred_7):
            assert pred_7 == ()
        case _:
            assert False

    match DatetimeStringValidator():
        case DatetimeStringValidator(pred_8):
            assert pred_8 == ()
        case _:
            assert False

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

    match AlwaysValid():
        case AlwaysValid():
            assert True
        case _:
            assert False
