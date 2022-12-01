from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID, uuid4

import pytest

from koda_validate import AlwaysValid, Invalid, MaxLength, StringValidator, Valid
from koda_validate.base import (
    ErrorDetail,
    InvalidCoercion,
    InvalidDict,
    InvalidPredicates,
    InvalidSimple,
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
    dc_v = DataclassValidator(PersonSimple)
    assert dc_v(None) == Invalid(
        dc_v, InvalidCoercion([dict, PersonSimple], PersonSimple)
    )


@pytest.mark.asyncio
async def test_will_fail_if_not_dataclass_async() -> None:
    dc_v = DataclassValidator(PersonSimple)
    assert await dc_v.validate_async(None) == Invalid(
        dc_v, InvalidCoercion([dict, PersonSimple], PersonSimple)
    )


def test_wrong_dataclass_is_invalid() -> None:
    @dataclass
    class Other:
        name: str
        age: int

    dc_v = DataclassValidator(PersonSimple)
    assert dc_v(Other("ok", 5)) == Invalid(
        dc_v, InvalidCoercion([dict, PersonSimple], PersonSimple)
    )


@pytest.mark.asyncio
async def test_wrong_dataclass_is_invalid_async() -> None:
    @dataclass
    class Other:
        name: str
        age: int

    dc_v = DataclassValidator(PersonSimple)
    assert await dc_v.validate_async(Other("ok", 5)) == Invalid(
        dc_v, InvalidCoercion([dict, PersonSimple], PersonSimple)
    )


def test_valid_dict_returns_dataclass_result() -> None:
    assert DataclassValidator(PersonSimple)({"name": "bob", "age": 100}) == Valid(
        PersonSimple("bob", 100)
    )


@pytest.mark.asyncio
async def test_valid_dict_returns_dataclass_result_async() -> None:
    assert await DataclassValidator(PersonSimple).validate_async(
        {"name": "bob", "age": 100}
    ) == Valid(PersonSimple("bob", 100))


def test_valid_dataclass_returns_dataclass_result() -> None:
    result = DataclassValidator(PersonSimple)(PersonSimple("alice", 99))

    assert result == Valid(PersonSimple("alice", 99))


@pytest.mark.asyncio
async def test_valid_dataclass_returns_dataclass_result_async() -> None:
    result = await DataclassValidator(PersonSimple).validate_async(
        PersonSimple("alice", 99)
    )

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
    assert v1(test_dict) == Invalid(
        v1,
        InvalidDict(
            {
                "first_name": Invalid(
                    v1.schema["first_name"], InvalidPredicates([MaxLength(3)])
                )
            }
        ),
    )


@pytest.mark.asyncio
async def test_explicit_overrides_work_async() -> None:
    @dataclass
    class A:
        first_name: str
        last_name: str

    test_dict = {"first_name": "longname", "last_name": "jones"}

    v0 = DataclassValidator(A)
    assert await v0.validate_async(test_dict) == Valid(A("longname", "jones"))

    v1 = DataclassValidator(A, overrides={"first_name": StringValidator(MaxLength(3))})
    assert await v1.validate_async(test_dict) == Invalid(
        v1,
        InvalidDict(
            {
                "first_name": Invalid(
                    v1.schema["first_name"], InvalidPredicates([MaxLength(3)])
                )
            }
        ),
    )


def test_validate_object_works() -> None:
    @dataclass
    class A:
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> Optional[ErrorDetail]:
        if obj.first_name == obj.last_name:
            return InvalidSimple("first name cannot be last name")
        return None

    v1 = DataclassValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert v1(test_dict_same) == Invalid(
        v1, InvalidSimple("first name cannot be last name")
    )

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert v1(test_dict_different) == Valid(A(**test_dict_different))

    # should also work with dataclasses
    test_dc_same = A("same", "same")
    assert v1(test_dc_same) == Invalid(
        v1, InvalidSimple("first name cannot be last name")
    )

    test_dc_different = A("different", "names")

    assert v1(test_dc_different) == Valid(test_dc_different)


@pytest.mark.asyncio
async def test_validate_object_works_async() -> None:
    @dataclass
    class A:
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> Optional[ErrorDetail]:
        if obj.first_name == obj.last_name:
            return InvalidSimple("first name cannot be last name")
        return None

    v1 = DataclassValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert await v1.validate_async(test_dict_same) == Invalid(
        v1, InvalidSimple("first name cannot be last name")
    )

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert await v1.validate_async(test_dict_different) == Valid(A(**test_dict_different))

    # should also work with dataclasses
    test_dc_same = A("same", "same")
    assert await v1.validate_async(test_dc_same) == Invalid(
        v1, InvalidSimple("first name cannot be last name")
    )

    test_dc_different = A("different", "names")

    assert await v1.validate_async(test_dc_different) == Valid(test_dc_different)


def test_validates_proper_string_type() -> None:
    @dataclass
    class Example:
        name: str

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example("ok")) == Valid(Example("ok"))

    # not type-safe, but still validate
    assert dc_validator(Example(5)) == Invalid(  # type: ignore
        dc_validator,
        InvalidDict(
            {"name": Invalid(dc_validator.schema["name"], InvalidType(str))},
        ),
    )


def test_validates_proper_int_type() -> None:
    @dataclass
    class Example:
        name: int

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(5)) == Valid(Example(5))
    # not type-safe, but still validate
    assert dc_validator(Example("bad")) == Invalid(  # type: ignore
        dc_validator,
        InvalidDict(
            {"name": Invalid(dc_validator.schema["name"], InvalidType(int))},
        ),
    )


def test_validates_proper_float_type() -> None:
    @dataclass
    class Example:
        name: float

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(5.0)) == Valid(Example(5.0))
    assert dc_validator(Example(5)) == Invalid(
        dc_validator,
        InvalidDict(
            {"name": Invalid(dc_validator.schema["name"], InvalidType(float))},
        ),
    )


def test_validates_proper_bool_type() -> None:
    @dataclass
    class Example:
        name: bool

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(False)) == Valid(Example(False))
    # not type-safe, but still validate
    assert dc_validator(Example(1)) == Invalid(  # type: ignore
        dc_validator,
        InvalidDict(
            {"name": Invalid(dc_validator.schema["name"], InvalidType(bool))},
        ),
    )


def test_validates_proper_decimal_type() -> None:
    @dataclass
    class Example:
        name: Decimal

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example(Decimal(4))) == Valid(Example(Decimal(4)))

    # not type-safe, but still validate
    assert dc_validator(Example(5.6)) == Invalid(  # type: ignore
        dc_validator,
        InvalidDict(
            {
                "name": Invalid(
                    dc_validator.schema["name"],
                    InvalidCoercion(
                        [str, int, Decimal],
                        Decimal,
                    ),
                )
            },
        ),
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
        dc_validator,
        InvalidDict(
            {
                "name": Invalid(
                    dc_validator.schema["name"], InvalidCoercion([str, UUID], UUID)
                )
            },
        ),
    )


def test_will_fail_if_not_exact_dataclass() -> None:
    @dataclass
    class Bad:
        name: str

    validator = DataclassValidator(PersonSimple)
    assert validator(Bad("hmm")) == Invalid(
        validator, InvalidCoercion([dict, PersonSimple], PersonSimple)
    )


def test_get_typehint_validator_bare_tuple() -> None:
    for t_validator in [get_typehint_validator(tuple), get_typehint_validator(Tuple)]:
        assert isinstance(t_validator, TupleHomogenousValidator)
        assert isinstance(t_validator.item_validator, AlwaysValid)
