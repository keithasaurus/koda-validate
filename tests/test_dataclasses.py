from dataclasses import dataclass
from decimal import Decimal
from typing import Tuple
from uuid import UUID, uuid4

from koda_validate import AlwaysValid, Invalid, MaxLength, StringValidator, Valid
from koda_validate.base import (
    InvalidCoercion,
    InvalidCustom,
    InvalidDict,
    InvalidType,
    ValidationResult,
)
from koda_validate.dataclasses import DataclassValidator, get_typehint_validator
from koda_validate.tuple import TupleHomogenousValidator


@dataclass
class PersonSimple:
    name: str
    age: int


def test_will_fail_if_not_dataclass() -> None:
    assert DataclassValidator(PersonSimple)(None) == Invalid(
        InvalidCoercion(
            [dict, PersonSimple], PersonSimple, "expected a dict or PersonSimple instance"
        )
    )


def test_wrong_dataclass_is_invalid() -> None:
    @dataclass
    class Other:
        name: str
        age: int

    assert DataclassValidator(PersonSimple)(Other("ok", 5)) == Invalid(
        InvalidCoercion(
            [dict, PersonSimple], PersonSimple, "expected a dict or PersonSimple instance"
        )
    )


def test_valid_dict_returns_dataclass_result() -> None:
    assert DataclassValidator(PersonSimple)({"name": "bob", "age": 100}) == Valid(
        PersonSimple("bob", 100)
    )


def test_valid_dataclass_returns_dataclass_result() -> None:
    result = DataclassValidator(PersonSimple)(PersonSimple("alice", 99))

    assert result == Valid(PersonSimple("alice", 99))


def test_explicit_overrides_work() -> None:
    @dataclass
    class A:
        first_name: str
        last_name: str

    test_dict = {"first_name": "longname", "last_name": "jones"}

    v0 = DataclassValidator(A)
    assert v0(test_dict) == Valid(A("longname", "jones"))

    v1 = DataclassValidator(A, overrides={"first_name": StringValidator(MaxLength(3))})
    assert v1(test_dict) == Invalid(InvalidDict({"first_name": [MaxLength(3)]}))


def test_validate_object_works() -> None:
    @dataclass
    class A:
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> ValidationResult[A]:
        if obj.first_name == obj.last_name:
            return Invalid(InvalidCustom("first name cannot be last name"))
        else:
            return Valid(obj)

    v1 = DataclassValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert v1(test_dict_same) == Invalid(InvalidCustom("first name cannot be last name"))

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert v1(test_dict_different) == Valid(A(**test_dict_different))

    # should also work with dataclasses
    test_dc_same = A("same", "same")
    assert v1(test_dc_same) == Invalid(InvalidCustom("first name cannot be last name"))

    test_dc_different = A("different", "names")

    assert v1(test_dc_different) == Valid(test_dc_different)


def test_validates_proper_string_type() -> None:
    @dataclass
    class Example:
        name: str

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example("ok")) == Valid(Example("ok"))

    # not type-safe, but still validate
    assert dc_validator(Example(5)) == Invalid(  # type: ignore
        InvalidDict({"name": InvalidType(str, "expected a string")})
    )


def test_validates_proper_int_type() -> None:
    @dataclass
    class Example:
        name: int

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(5)) == Valid(Example(5))
    # not type-safe, but still validate
    assert dc_validator(Example("bad")) == Invalid(  # type: ignore
        InvalidDict({"name": InvalidType(int, "expected an integer")})
    )


def test_validates_proper_float_type() -> None:
    @dataclass
    class Example:
        name: float

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(5.0)) == Valid(Example(5.0))
    assert dc_validator(Example(5)) == Invalid(
        InvalidDict({"name": InvalidType(float, "expected a float")})
    )


def test_validates_proper_bool_type() -> None:
    @dataclass
    class Example:
        name: bool

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(False)) == Valid(Example(False))
    # not type-safe, but still validate
    assert dc_validator(Example(1)) == Invalid(  # type: ignore
        InvalidDict({"name": InvalidType(bool, "expected a boolean")})
    )


def test_validates_proper_decimal_type() -> None:
    @dataclass
    class Example:
        name: Decimal

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(Decimal(4))) == Valid(Example(Decimal(4)))

    # not type-safe, but still validate
    assert dc_validator(Example(5.6)) == Invalid(  # type: ignore
        InvalidDict(
            {
                "name": InvalidCoercion(
                    [str, int, Decimal],
                    Decimal,
                    "expected a Decimal, or a Decimal-compatible string or integer",
                )
            }
        )
    )


def test_validates_proper_uuid_type() -> None:
    @dataclass
    class Example:
        name: UUID

    dc_validator = DataclassValidator(Example)
    test_uuid = uuid4()
    assert dc_validator(Example(test_uuid)) == Valid(Example(test_uuid))

    # not type-safe, but should still validate
    assert dc_validator(Example(str(test_uuid))) == Valid(  # type: ignore
        Example(test_uuid)
    )

    assert dc_validator(Example(123)) == Invalid(  # type: ignore
        InvalidDict(
            {
                "name": InvalidCoercion(
                    [str, UUID], UUID, "expected a UUID, or a UUID-compatible string"
                )
            }
        )
    )


def test_will_fail_if_not_exact_dataclass() -> None:
    @dataclass
    class Bad:
        name: str

    assert DataclassValidator(PersonSimple)(Bad("hmm")) == Invalid(
        InvalidCoercion(
            [dict, PersonSimple], PersonSimple, "expected a dict or PersonSimple instance"
        )
    )


def test_get_typehint_validator_bare_tuple() -> None:
    for t_validator in [get_typehint_validator(tuple), get_typehint_validator(Tuple)]:
        assert isinstance(t_validator, TupleHomogenousValidator)
        assert isinstance(t_validator.item_validator, AlwaysValid)
