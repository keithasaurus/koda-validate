from decimal import Decimal
from typing import NamedTuple, Optional
from uuid import UUID, uuid4

import pytest

from koda_validate import Invalid, MaxLength, StringValidator, Valid
from koda_validate.base import (
    BasicErr,
    CoercionErr,
    ErrType,
    ExtraKeysErr,
    KeyErrs,
    PredicateErrs,
    TypeErr,
    missing_key_err,
)
from koda_validate.namedtuple import NamedTupleValidator


class PersonSimple(NamedTuple):
    name: str
    age: int


def test_will_fail_if_not_namedtuple() -> None:
    dc_v = NamedTupleValidator(PersonSimple)
    assert dc_v(None) == Invalid(
        CoercionErr({dict, PersonSimple}, PersonSimple), None, dc_v
    )


@pytest.mark.asyncio
async def test_will_fail_if_not_namedtuple_async() -> None:
    dc_v = NamedTupleValidator(PersonSimple)
    assert await dc_v.validate_async(None) == Invalid(
        CoercionErr({dict, PersonSimple}, PersonSimple), None, dc_v
    )


def test_wrong_namedtuple_is_invalid() -> None:
    class Other(NamedTuple):
        name: str
        age: int

    dc_v = NamedTupleValidator(PersonSimple)
    assert dc_v(Other("ok", 5)) == Invalid(
        CoercionErr({dict, PersonSimple}, PersonSimple), Other("ok", 5), dc_v
    )


@pytest.mark.asyncio
async def test_wrong_namedtuple_is_invalid_async() -> None:
    class Other(NamedTuple):
        name: str
        age: int

    dc_v = NamedTupleValidator(PersonSimple)
    assert await dc_v.validate_async(Other("ok", 5)) == Invalid(
        CoercionErr({dict, PersonSimple}, PersonSimple), Other("ok", 5), dc_v
    )


def test_valid_dict_returns_namedtuple_result() -> None:
    assert NamedTupleValidator(PersonSimple)({"name": "bob", "age": 100}) == Valid(
        PersonSimple("bob", 100)
    )


@pytest.mark.asyncio
async def test_valid_dict_returns_namedtuple_result_async() -> None:
    assert await NamedTupleValidator(PersonSimple).validate_async(
        {"name": "bob", "age": 100}
    ) == Valid(PersonSimple("bob", 100))


def test_valid_namedtuple_returns_namedtuple_result() -> None:
    result = NamedTupleValidator(PersonSimple)(PersonSimple("alice", 99))

    assert result == Valid(PersonSimple("alice", 99))


@pytest.mark.asyncio
async def test_valid_namedtuple_returns_namedtuple_result_async() -> None:
    result = await NamedTupleValidator(PersonSimple).validate_async(
        PersonSimple("alice", 99)
    )

    assert result == Valid(PersonSimple("alice", 99))


def test_explicit_overrides_work() -> None:
    class A(NamedTuple):
        first_name: str
        last_name: str

    test_dict = {"first_name": "longname", "last_name": "jones"}

    v0 = NamedTupleValidator(A)
    assert v0(test_dict) == Valid(A("longname", "jones"))

    v1 = NamedTupleValidator(A, overrides={"first_name": StringValidator(MaxLength(3))})
    assert v1(test_dict) == Invalid(
        KeyErrs(
            {
                "first_name": Invalid(
                    PredicateErrs([MaxLength(3)]), "longname", v1.schema["first_name"]
                )
            }
        ),
        test_dict,
        v1,
    )


@pytest.mark.asyncio
async def test_explicit_overrides_work_async() -> None:
    class A(NamedTuple):
        first_name: str
        last_name: str

    test_dict = {"first_name": "longname", "last_name": "jones"}

    v0 = NamedTupleValidator(A)
    assert await v0.validate_async(test_dict) == Valid(A("longname", "jones"))

    v1 = NamedTupleValidator(A, overrides={"first_name": StringValidator(MaxLength(3))})
    assert await v1.validate_async(test_dict) == Invalid(
        KeyErrs(
            {
                "first_name": Invalid(
                    PredicateErrs([MaxLength(3)]), "longname", v1.schema["first_name"]
                )
            }
        ),
        test_dict,
        v1,
    )


def test_validate_object_works() -> None:
    class A(NamedTuple):
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> Optional[ErrType]:
        if obj.first_name == obj.last_name:
            return BasicErr("first name cannot be last name")
        return None

    v1 = NamedTupleValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert v1(test_dict_same) == Invalid(
        BasicErr("first name cannot be last name"), A("same", "same"), v1
    )

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert v1(test_dict_different) == Valid(A(**test_dict_different))

    # should also work with namedtuplees
    test_dc_same = A("same", "same")
    assert v1(test_dc_same) == Invalid(
        BasicErr("first name cannot be last name"), test_dc_same, v1
    )

    test_dc_different = A("different", "names")

    assert v1(test_dc_different) == Valid(test_dc_different)


@pytest.mark.asyncio
async def test_validate_object_works_async() -> None:
    class A(NamedTuple):
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> Optional[ErrType]:
        if obj.first_name == obj.last_name:
            return BasicErr("first name cannot be last name")
        return None

    v1 = NamedTupleValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert await v1.validate_async(test_dict_same) == Invalid(
        BasicErr("first name cannot be last name"), A("same", "same"), v1
    )

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert await v1.validate_async(test_dict_different) == Valid(A(**test_dict_different))

    # should also work with namedtuplees
    test_dc_same = A("same", "same")
    assert await v1.validate_async(test_dc_same) == Invalid(
        BasicErr("first name cannot be last name"), test_dc_same, v1
    )

    test_dc_different = A("different", "names")

    assert await v1.validate_async(test_dc_different) == Valid(test_dc_different)


def test_validates_proper_string_type() -> None:
    class Example(NamedTuple):
        name: str

    nt_validator = NamedTupleValidator(Example)

    assert nt_validator(Example("ok")) == Valid(Example("ok"))

    # not type-safe, but still validate
    assert nt_validator(Example(5)) == Invalid(  # type: ignore
        KeyErrs(
            {"name": Invalid(TypeErr(str), 5, nt_validator.schema["name"])},
        ),
        {"name": 5},
        nt_validator,
    )


def test_validates_proper_int_type() -> None:
    class Example(NamedTuple):
        name: int

    nt_validator = NamedTupleValidator(Example)

    assert nt_validator(Example(5)) == Valid(Example(5))
    # not type-safe, but still validate
    assert nt_validator(Example("bad")) == Invalid(  # type: ignore
        KeyErrs(
            {"name": Invalid(TypeErr(int), "bad", nt_validator.schema["name"])},
        ),
        {"name": "bad"},
        nt_validator,
    )


def test_validates_proper_float_type() -> None:
    class Example(NamedTuple):
        name: float

    nt_validator = NamedTupleValidator(Example)

    assert nt_validator(Example(5.0)) == Valid(Example(5.0))
    assert nt_validator(Example(5)) == Invalid(
        KeyErrs(
            {"name": Invalid(TypeErr(float), 5, nt_validator.schema["name"])},
        ),
        {"name": 5},
        nt_validator,
    )


def test_validates_proper_bool_type() -> None:
    class Example(NamedTuple):
        name: bool

    nt_validator = NamedTupleValidator(Example)

    assert nt_validator(Example(False)) == Valid(Example(False))
    # not type-safe, but still validate
    assert nt_validator(Example(1)) == Invalid(  # type: ignore
        KeyErrs(
            {"name": Invalid(TypeErr(bool), 1, nt_validator.schema["name"])},
        ),
        {"name": 1},
        nt_validator,
    )


def test_validates_proper_decimal_type() -> None:
    class Example(NamedTuple):
        name: Decimal

    nt_validator = NamedTupleValidator(Example)

    assert nt_validator(Example(Decimal(4))) == Valid(Example(Decimal(4)))

    # not type-safe, but still validate
    assert nt_validator(Example(5.6)) == Invalid(  # type: ignore
        KeyErrs(
            {
                "name": Invalid(
                    CoercionErr(
                        {str, int, Decimal},
                        Decimal,
                    ),
                    5.6,
                    nt_validator.schema["name"],
                )
            },
        ),
        {"name": 5.6},
        nt_validator,
    )


def test_validates_proper_uuid_type() -> None:
    class Example(NamedTuple):
        name: UUID

    nt_validator = NamedTupleValidator(Example)
    test_uuid = uuid4()
    assert nt_validator(Example(test_uuid)) == Valid(Example(test_uuid))

    # not type-safe, but should still validate
    assert nt_validator(Example(str(test_uuid))) == Valid(  # type: ignore
        Example(test_uuid)
    )

    assert nt_validator(Example(123)) == Invalid(  # type: ignore
        KeyErrs(
            {
                "name": Invalid(
                    CoercionErr({str, UUID}, UUID), 123, nt_validator.schema["name"]
                )
            },
        ),
        Example(123)._asdict(),  # type: ignore
        nt_validator,
    )


def test_will_fail_if_not_exact_namedtuple() -> None:
    class Bad(NamedTuple):
        name: str

    validator = NamedTupleValidator(PersonSimple)
    assert validator(Bad("hmm")) == Invalid(
        CoercionErr({dict, PersonSimple}, PersonSimple), Bad("hmm"), validator
    )


def test_can_handle_default_arguments() -> None:
    class NameCls(NamedTuple):
        name: str = "ok"

    validator = NamedTupleValidator(NameCls)
    assert validator(NameCls("hmm")) == Valid(NameCls("hmm"))
    assert validator({}) == Valid(NameCls("ok"))
    assert validator({"name": "set value"}) == Valid(NameCls("set value"))


def test_can_handle_basic_str_types() -> None:
    class Bad(NamedTuple):
        name: "str"

    validator = NamedTupleValidator(PersonSimple)
    assert validator(Bad("hmm")) == Invalid(
        CoercionErr({dict, PersonSimple}, PersonSimple), Bad("hmm"), validator
    )


def test_repr() -> None:
    class A(NamedTuple):
        name: str

    assert repr(NamedTupleValidator(A)) == f"NamedTupleValidator({repr(A)})"

    def obj_fn(obj: A) -> Optional[ErrType]:
        return None

    assert repr(NamedTupleValidator(A, validate_object=obj_fn)) == (
        f"NamedTupleValidator({repr(A)}, validate_object={repr(obj_fn)})"
    )

    overrides_str = "overrides={'name': StringValidator()}"
    assert repr(
        NamedTupleValidator(
            A, overrides={"name": StringValidator()}, validate_object=obj_fn
        )
    ) == (
        f"NamedTupleValidator({repr(A)}, {overrides_str}, validate_object={repr(obj_fn)})"
    )


def test_eq() -> None:
    class A(NamedTuple):
        name: str

    class B(NamedTuple):
        name: str
        age: int

    assert NamedTupleValidator(A) == NamedTupleValidator(A)
    assert NamedTupleValidator(A) != NamedTupleValidator(B)
    assert NamedTupleValidator(A) == NamedTupleValidator(A, overrides={})
    assert NamedTupleValidator(A, overrides={}) == NamedTupleValidator(A, overrides={})
    assert NamedTupleValidator(
        A, overrides={"name": StringValidator()}
    ) == NamedTupleValidator(A, overrides={})
    assert NamedTupleValidator(
        A, overrides={"name": StringValidator()}
    ) == NamedTupleValidator(A, overrides={"name": StringValidator()})

    def obj_fn(obj: A) -> Optional[ErrType]:
        return None

    assert NamedTupleValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    ) != NamedTupleValidator(A, overrides={"name": StringValidator()})

    assert NamedTupleValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    ) == NamedTupleValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    )

    def obj_fn_2(obj: A) -> Optional[ErrType]:
        return None

    assert NamedTupleValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    ) != NamedTupleValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn_2
    )


def test_extra_keys_invalid() -> None:
    v = NamedTupleValidator(PersonSimple)

    test_d = {"name": "ok", "d": "whatever"}
    assert v(test_d) == Invalid(ExtraKeysErr({"age", "name"}), test_d, v)


@pytest.mark.asyncio
async def test_extra_keys_invalid_async() -> None:
    v = NamedTupleValidator(PersonSimple)

    test_d = {"name": "ok", "d": "whatever"}
    assert await v.validate_async(test_d) == Invalid(
        ExtraKeysErr({"age", "name"}), test_d, v
    )


def test_missing_key() -> None:
    v = NamedTupleValidator(PersonSimple)

    test_d = {"name": "ok"}
    assert v(test_d) == Invalid(
        KeyErrs({"age": Invalid(missing_key_err, test_d, v)}), test_d, v
    )


@pytest.mark.asyncio
async def test_missing_key_async() -> None:
    v = NamedTupleValidator(PersonSimple)

    test_d = {"name": "ok"}
    assert await v.validate_async(test_d) == Invalid(
        KeyErrs({"age": Invalid(missing_key_err, test_d, v)}), test_d, v
    )