from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from koda_validate import (
    AlwaysValid,
    BoolValidator,
    DecimalValidator,
    FloatValidator,
    IntValidator,
    Invalid,
    ListValidator,
    MapValidator,
    NoneValidator,
    StringValidator,
    Valid,
)
from koda_validate.dataclasses import DataclassValidator, get_typehint_validator
from koda_validate.tuple import TupleHomogenousValidator
from koda_validate.union import UnionValidatorAny


@dataclass
class PersonSimple:
    name: str
    age: int


def test_will_fail_if_not_dataclass() -> None:
    assert DataclassValidator(PersonSimple)(None) == Invalid(
        ["expected a dict or PersonSimple instance"]
    )


def test_wrong_dataclass_is_invalid() -> None:
    @dataclass
    class Other:
        name: str
        age: int

    assert DataclassValidator(PersonSimple)(Other("ok", 5)) == Invalid(
        ["expected a dict or PersonSimple instance"]
    )


def test_valid_dict_returns_dataclass_result() -> None:
    assert DataclassValidator(PersonSimple)({"name": "bob", "age": 100}) == Valid(
        PersonSimple("bob", 100)
    )


def test_valid_dataclass_returns_dataclass_result() -> None:
    result = DataclassValidator(PersonSimple)(PersonSimple("alice", 99))

    assert result == Valid(PersonSimple("alice", 99))


def test_validates_proper_string_type() -> None:
    @dataclass
    class Example:
        name: str

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example("ok")) == Valid(Example("ok"))
    assert dc_validator(Example(5)) == Invalid({"name": ["expected a string"]})


def test_validates_proper_int_type() -> None:
    @dataclass
    class Example:
        name: int

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(5)) == Valid(Example(5))
    assert dc_validator(Example("bad")) == Invalid({"name": ["expected an integer"]})


def test_validates_proper_float_type() -> None:
    @dataclass
    class Example:
        name: float

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(5.0)) == Valid(Example(5.0))
    assert dc_validator(Example(5)) == Invalid({"name": ["expected a float"]})


def test_validates_proper_bool_type() -> None:
    @dataclass
    class Example:
        name: bool

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(False)) == Valid(Example(False))
    assert dc_validator(Example(1)) == Invalid({"name": ["expected a boolean"]})


def test_validates_proper_decimal_type() -> None:
    @dataclass
    class Example:
        name: Decimal

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(Decimal(4))) == Valid(Example(Decimal(4)))
    assert dc_validator(Example(5.6)) == Invalid(
        {"name": ["expected a Decimal, or a Decimal-compatible string or integer"]}
    )


def test_validates_proper_uuid_type() -> None:
    @dataclass
    class Example:
        name: UUID

    dc_validator = DataclassValidator(Example)
    test_uuid = uuid4()
    assert dc_validator(Example(test_uuid)) == Valid(Example(test_uuid))
    assert dc_validator(Example(str(test_uuid))) == Valid(Example(test_uuid))
    assert dc_validator(Example(123)) == Invalid(
        {"name": ["expected a UUID, or a UUID-compatible string"]}
    )


def test_will_fail_if_not_exact_dataclass() -> None:
    @dataclass
    class Bad:
        name: str

    assert DataclassValidator(PersonSimple)(Bad("hmm")) == Invalid(
        ["expected a dict or PersonSimple instance"]
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
    ) == Invalid({"name": ["key missing"]})

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
    ) == Invalid({"a": {"something": {"5": {"key_error": ["expected a string"]}}}})


def test_complex_union_dataclass() -> None:
    @dataclass
    class Example:
        a: Optional[str] | float | int

    example_validator = DataclassValidator(Example)
    assert example_validator({"a": "ok"}) == Valid(Example("ok"))
    assert example_validator({"a": None}) == Valid(Example(None))
    assert example_validator({"a": 1.1}) == Valid(Example(1.1))
    assert example_validator({"a": 5}) == Valid(Example(5))
    assert example_validator({"a": False}) == Invalid(
        {
            "a": {
                "variant 1": ["expected a string"],
                "variant 2": ["expected None"],
                "variant 3": ["expected a float"],
                "variant 4": ["expected an integer"],
            }
        }
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
    assert isinstance(union_str_int_validator.validators[0], StringValidator)
    assert isinstance(union_str_int_validator.validators[1], IntValidator)
    assert isinstance(union_str_int_validator.validators[2], BoolValidator)

    union_opt_str_int_validator = get_typehint_validator(Union[Optional[str], int, bool])
    assert len(union_opt_str_int_validator.validators) == 4
    assert isinstance(union_opt_str_int_validator, UnionValidatorAny)
    assert isinstance(union_opt_str_int_validator.validators[0], StringValidator)
    assert isinstance(union_opt_str_int_validator.validators[1], NoneValidator)
    assert isinstance(union_opt_str_int_validator.validators[2], IntValidator)
    assert isinstance(union_opt_str_int_validator.validators[3], BoolValidator)


def test_get_typehint_validator_tuple() -> None:
    tuple_homogeneous_validator_1 = get_typehint_validator(tuple[str, ...])
    assert isinstance(tuple_homogeneous_validator_1, TupleHomogenousValidator)
    assert isinstance(tuple_homogeneous_validator_1.item_validator, StringValidator)
