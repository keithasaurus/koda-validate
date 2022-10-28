from dataclasses import dataclass

from koda import Err, Ok, Result

from koda_validate import (
    BooleanValidator,
    DecimalValidator,
    IntValidator,
    IsDictValidator,
    MapValidator,
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
