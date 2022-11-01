import re
from dataclasses import dataclass
from typing import Any, Dict, Hashable

from koda import Err, Ok, Result

from koda_validate import (
    BoolValidator,
    Choices,
    DatetimeValidator,
    DateValidator,
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
    DictValidator,
    DictValidatorAny,
    MaxKeys,
    MinKeys,
    is_dict_validator,
    key,
)
from koda_validate.tuple import Tuple2Validator, Tuple3Validator


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

    match MapValidator((str_ := StringValidator()), (int_ := IntValidator())):
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

    @dataclass
    class Person:
        name: str
        age: int

    def validate_person(p: Person) -> Result[Person, Serializable]:
        if len(p.name) > p.age:
            return Err(["your name cannot be longer than your name"])
        else:
            return Ok(p)

    dv_validator: DictValidator[Person] = DictValidator(
        (into_ := Person),
        (str_1 := key("name", StringValidator())),
        (int_1 := key("age", IntValidator())),
        validate_object=validate_person,
    )
    match dv_validator:
        case DictValidator(into, fields, validate_object):
            assert into == into_
            assert fields[0] == str_1
            assert fields[1] == int_1
            assert validate_object == validate_person

        case _:
            assert False

    def validate_person_dict_any(
        p: Dict[Hashable, Any]
    ) -> Result[Dict[Hashable, Any], Serializable]:
        if len(p["name"]) > p["age"]:
            return Err(["your name cannot be longer than your name"])
        else:
            return Ok(p)

    dvu_validator: DictValidatorAny = DictValidatorAny(
        (str_0 := key("name", StringValidator())),
        (int_0 := key("age", IntValidator())),
        validate_object=validate_person_dict_any,
    )
    match dvu_validator:
        case DictValidatorAny(fields, validate_object):
            assert into == into_
            assert fields[0] == str_0
            assert fields[1] == int_0
            assert validate_object == validate_person_dict_any

        case _:
            assert False

    match FloatValidator():
        case FloatValidator(preds):
            assert preds == ()
        case _:
            assert False

    def lazy_dv_validator() -> DictValidator[Person]:
        return dv_validator_2

    dv_validator_2: DictValidator[Person] = DictValidator(
        Person,
        key("name", StringValidator()),
        key("age", IntValidator()),
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
        case ExactValidator(match, preprocessors):
            assert match == "abc"
            assert preprocessors is None

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

    match DateValidator():
        case DateValidator(pred_7):
            assert pred_7 == ()
        case _:
            assert False

    match DatetimeValidator():
        case DatetimeValidator(pred_8):
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
