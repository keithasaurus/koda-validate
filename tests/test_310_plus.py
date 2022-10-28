from dataclasses import dataclass

from koda import Err, Ok, Result

from koda_validate import (
    BooleanValidator,
    Choices,
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
    Min,
    MinItems,
    MultipleOf,
    OptionalValidator,
    Serializable,
    StringValidator,
)
from koda_validate.dictionary import (
    DictValidator,
    MaxKeys,
    MinKeys,
    is_dict_validator,
    key,
)


def test_match_args() -> None:
    match BooleanValidator():
        case BooleanValidator(predicates_bool):
            assert predicates_bool == ()
        case _:
            assert False

    match DecimalValidator():
        case DecimalValidator(predicates_decimal):
            assert predicates_decimal == ()
        case _:
            assert False

    match MapValidator((str_ := StringValidator()), (int_ := IntValidator())):
        case MapValidator(string_validator, int_validator, predicates_map):
            assert string_validator == str_
            assert int_validator == int_
            assert predicates_map == ()

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

    match ListValidator((str_vldtr := StringValidator()), (min_items_ := MinItems(2))):
        case ListValidator(item_validator, predicates):
            assert item_validator is str_vldtr
            assert predicates == (min_items_,)

    match OptionalValidator(str_3 := StringValidator()):
        case OptionalValidator(opt_validator):
            assert opt_validator is str_3

        case _:
            assert False
