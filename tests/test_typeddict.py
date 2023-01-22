import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, TypedDict
from uuid import UUID, uuid4

import pytest
from koda import Just, Maybe, nothing

from koda_validate import (
    CoercionErr,
    ExtraKeysErr,
    IndexErrs,
    IntValidator,
    Invalid,
    KeyErrs,
    ListValidator,
    MaxLength,
    PredicateErrs,
    StringValidator,
    TypeErr,
    Valid,
)
from koda_validate.base import Coercer
from koda_validate.errors import ErrType, missing_key_err
from koda_validate.serialization import SerializableErr
from koda_validate.typeddict import TypedDictValidator


class PersonSimpleTD(TypedDict):
    name: str
    age: int


def test_valid_dict_returns_typeddict_result() -> None:
    assert TypedDictValidator(PersonSimpleTD)({"name": "bob", "age": 100}) == Valid(
        {"name": "bob", "age": 100}
    )


def test_nested_typeddict() -> None:
    class Group(TypedDict):
        group_name: str
        people: List[PersonSimpleTD]

    valid_dict = {
        "group_name": "some_group",
        "people": [
            {"name": "alice", "age": 1},
            {"name": "bob", "age": 10},
        ],
    }
    v = TypedDictValidator(Group)

    assert v(valid_dict) == Valid(valid_dict)
    assert v({}) == Invalid(
        err_type=KeyErrs(
            keys={
                "group_name": Invalid(err_type=missing_key_err, value={}, validator=v),
                "people": Invalid(missing_key_err, value={}, validator=v),
            }
        ),
        value={},
        validator=v,
    )
    assert v(
        {"group_name": "something", "people": ["bad", {"name": 1, "age": "2"}]}
    ) == Invalid(
        err_type=KeyErrs(
            keys={
                "people": Invalid(
                    IndexErrs(
                        {
                            0: Invalid(
                                TypeErr(dict), "bad", TypedDictValidator(PersonSimpleTD)
                            ),
                            1: Invalid(
                                KeyErrs(
                                    keys={
                                        "age": Invalid(
                                            TypeErr(expected_type=int),
                                            "2",
                                            IntValidator(),
                                        ),
                                        "name": Invalid(
                                            TypeErr(expected_type=str),
                                            1,
                                            StringValidator(),
                                        ),
                                    }
                                ),
                                {"age": "2", "name": 1},
                                TypedDictValidator(PersonSimpleTD),
                            ),
                        }
                    ),
                    ["bad", {"age": "2", "name": 1}],
                    ListValidator(TypedDictValidator(PersonSimpleTD)),
                )
            }
        ),
        value={"group_name": "something", "people": ["bad", {"age": "2", "name": 1}]},
        validator=v,
    )


@pytest.mark.asyncio
async def test_valid_dict_returns_typeddict_result_async() -> None:
    assert await TypedDictValidator(PersonSimpleTD).validate_async(
        {"name": "bob", "age": 100}
    ) == Valid({"name": "bob", "age": 100})


def test_will_fail_if_not_typeddict() -> None:
    td_v = TypedDictValidator(PersonSimpleTD)
    assert td_v(None) == Invalid(TypeErr(dict), None, td_v)


@pytest.mark.asyncio
async def test_will_fail_if_not_typeddict_async() -> None:
    td_v = TypedDictValidator(PersonSimpleTD)
    assert await td_v.validate_async(None) == Invalid(TypeErr(dict), None, td_v)


def test_valid_typeddict_returns_typeddict_result() -> None:
    result = TypedDictValidator(PersonSimpleTD)(PersonSimpleTD(name="alice", age=99))

    assert result == Valid(PersonSimpleTD(name="alice", age=99))


@pytest.mark.asyncio
async def test_valid_typeddict_returns_typeddict_result_async() -> None:
    result = await TypedDictValidator(PersonSimpleTD).validate_async(
        {"name": "alice", "age": 99}
    )

    assert result == Valid(PersonSimpleTD(name="alice", age=99))


def test_extra_keys_invalid() -> None:
    v = TypedDictValidator(PersonSimpleTD, fail_on_unknown_keys=True)

    test_d = {"name": "ok", "d": "whatever"}
    assert v(test_d) == Invalid(ExtraKeysErr({"age", "name"}), test_d, v)


@pytest.mark.asyncio
async def test_extra_keys_invalid_async() -> None:
    v = TypedDictValidator(PersonSimpleTD, fail_on_unknown_keys=True)

    test_d = {"name": "ok", "d": "whatever"}
    assert await v.validate_async(test_d) == Invalid(
        ExtraKeysErr({"age", "name"}), test_d, v
    )


@pytest.mark.asyncio
async def test_missing_key_async() -> None:
    v = TypedDictValidator(PersonSimpleTD)

    test_d = {"name": "ok"}
    assert await v.validate_async(test_d) == Invalid(
        KeyErrs({"age": Invalid(missing_key_err, test_d, v)}), test_d, v
    )


def test_invalid_class_raises_error() -> None:
    @dataclass
    class DC:
        a: str

    for t in [DC, dict, set, list, tuple]:
        try:
            TypedDictValidator(t)
        except TypeError as e:
            assert str(e) == "must be a TypedDict subclass"
        else:
            raise AssertionError("init shouldn't succeed!")


def test_explicit_overrides_work() -> None:
    class A(TypedDict):
        first_name: str
        last_name: str

    test_dict = {"first_name": "longname", "last_name": "jones"}

    v0 = TypedDictValidator(A)
    assert v0(test_dict) == Valid(A(first_name="longname", last_name="jones"))

    v1 = TypedDictValidator(A, overrides={"first_name": StringValidator(MaxLength(3))})
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
    class A(TypedDict):
        first_name: str
        last_name: str

    test_dict = {"first_name": "longname", "last_name": "jones"}

    v0 = TypedDictValidator(A)
    assert await v0.validate_async(test_dict) == Valid(
        A(first_name="longname", last_name="jones")
    )

    v1 = TypedDictValidator(A, overrides={"first_name": StringValidator(MaxLength(3))})
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
    class A(TypedDict):
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> Optional[ErrType]:
        if obj["first_name"] == obj["last_name"]:
            return SerializableErr("first name cannot be last name")
        return None

    v1 = TypedDictValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert v1(test_dict_same) == Invalid(
        SerializableErr("first name cannot be last name"),
        A(first_name="same", last_name="same"),
        v1,
    )

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert v1(test_dict_different) == Valid(test_dict_different)

    # should also work with typeddictes
    test_dc_same = A(first_name="same", last_name="same")
    assert v1(test_dc_same) == Invalid(
        SerializableErr("first name cannot be last name"), test_dc_same, v1
    )

    test_dc_different = A(first_name="different", last_name="names")

    assert v1(test_dc_different) == Valid(test_dc_different)


@pytest.mark.asyncio
async def test_validate_object_works_async() -> None:
    class A(TypedDict):
        first_name: str
        last_name: str

    def first_name_last_name_are_different(obj: A) -> Optional[ErrType]:
        if obj["first_name"] == obj["last_name"]:
            return SerializableErr("first name cannot be last name")
        return None

    v1 = TypedDictValidator(A, validate_object=first_name_last_name_are_different)
    test_dict_same = {"first_name": "same", "last_name": "same"}
    assert await v1.validate_async(test_dict_same) == Invalid(
        SerializableErr("first name cannot be last name"),
        A(first_name="same", last_name="same"),
        v1,
    )

    test_dict_different = {"first_name": "different", "last_name": "names"}

    assert await v1.validate_async(test_dict_different) == Valid(test_dict_different)

    # should also work with typeddictes
    test_dc_same = A(first_name="same", last_name="same")
    assert await v1.validate_async(test_dc_same) == Invalid(
        SerializableErr("first name cannot be last name"), test_dc_same, v1
    )

    test_dc_different = A(first_name="different", last_name="names")

    assert await v1.validate_async(test_dc_different) == Valid(test_dc_different)


def test_validates_proper_string_type() -> None:
    class Example(TypedDict):
        name: str

    nt_validator = TypedDictValidator(Example)

    assert nt_validator({"name": "ok"}) == Valid(Example(name="ok"))

    # not type-safe, but still validate
    assert nt_validator(Example(name=5)) == Invalid(  # type: ignore
        KeyErrs(
            {"name": Invalid(TypeErr(str), 5, nt_validator.schema["name"])},
        ),
        {"name": 5},
        nt_validator,
    )


def test_validates_proper_int_type() -> None:
    class Example(TypedDict):
        name: int

    nt_validator = TypedDictValidator(Example)

    assert nt_validator(Example(name=5)) == Valid(Example(name=5))
    # not type-safe, but still validate
    assert nt_validator(Example(name="bad")) == Invalid(  # type: ignore
        KeyErrs(
            {"name": Invalid(TypeErr(int), "bad", nt_validator.schema["name"])},
        ),
        {"name": "bad"},
        nt_validator,
    )


def test_validates_proper_float_type() -> None:
    class Example(TypedDict):
        name: float

    nt_validator = TypedDictValidator(Example)

    assert nt_validator(Example(name=5.0)) == Valid(Example(name=5.0))
    assert nt_validator(Example(name=5)) == Invalid(
        KeyErrs(
            {"name": Invalid(TypeErr(float), 5, nt_validator.schema["name"])},
        ),
        {"name": 5},
        nt_validator,
    )


def test_validates_proper_bool_type() -> None:
    class Example(TypedDict):
        name: bool

    nt_validator = TypedDictValidator(Example)

    assert nt_validator(Example(name=False)) == Valid(Example(name=False))
    # not type-safe, but still validate
    assert nt_validator(Example(name=1)) == Invalid(  # type: ignore
        KeyErrs(
            {"name": Invalid(TypeErr(bool), 1, nt_validator.schema["name"])},
        ),
        {"name": 1},
        nt_validator,
    )


def test_validates_proper_decimal_type() -> None:
    class Example(TypedDict):
        name: Decimal

    nt_validator = TypedDictValidator(Example)

    assert nt_validator(Example(name=Decimal(4))) == Valid(Example(name=Decimal(4)))

    # not type-safe, but still validate
    assert nt_validator({"name": 5.6}) == Invalid(
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
    class Example(TypedDict):
        name: UUID

    nt_validator = TypedDictValidator(Example)
    test_uuid = uuid4()
    assert nt_validator(Example(name=test_uuid)) == Valid({"name": test_uuid})

    # not type-safe, but should still validate
    assert nt_validator(Example(name=str(test_uuid))) == Valid(  # type: ignore
        Example(name=test_uuid)
    )

    assert nt_validator(Example(name=123)) == Invalid(  # type: ignore
        KeyErrs(
            {
                "name": Invalid(
                    CoercionErr({str, UUID}, UUID), 123, nt_validator.schema["name"]
                )
            },
        ),
        Example(name=123),  # type: ignore
        nt_validator,
    )


def test_repr() -> None:
    class A(TypedDict):
        name: str

    assert repr(TypedDictValidator(A)) == f"TypedDictValidator({repr(A)})"
    assert (
        repr(TypedDictValidator(A, fail_on_unknown_keys=True))
        == f"TypedDictValidator({repr(A)}, fail_on_unknown_keys=True)"
    )

    def obj_fn(obj: A) -> Optional[ErrType]:
        return None

    assert repr(TypedDictValidator(A, validate_object=obj_fn)) == (
        f"TypedDictValidator({repr(A)}, validate_object={repr(obj_fn)})"
    )

    overrides_str = "overrides={'name': StringValidator()}"
    assert repr(
        TypedDictValidator(
            A, overrides={"name": StringValidator()}, validate_object=obj_fn
        )
    ) == (
        f"TypedDictValidator({repr(A)}, {overrides_str}, validate_object={repr(obj_fn)})"
    )


def test_eq() -> None:
    class A(TypedDict):
        name: str

    class B(TypedDict):
        name: str
        age: int

    assert TypedDictValidator(A) == TypedDictValidator(A)
    assert TypedDictValidator(A) != TypedDictValidator(A, fail_on_unknown_keys=True)
    assert TypedDictValidator(A) != TypedDictValidator(B)
    assert TypedDictValidator(A) == TypedDictValidator(A, overrides={})
    assert TypedDictValidator(A, overrides={}) == TypedDictValidator(A, overrides={})
    assert TypedDictValidator(
        A, overrides={"name": StringValidator()}
    ) == TypedDictValidator(A, overrides={})
    assert TypedDictValidator(
        A, overrides={"name": StringValidator()}
    ) == TypedDictValidator(A, overrides={"name": StringValidator()})

    def obj_fn(obj: A) -> Optional[ErrType]:
        return None

    assert TypedDictValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    ) != TypedDictValidator(A, overrides={"name": StringValidator()})

    assert TypedDictValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    ) == TypedDictValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    )

    def obj_fn_2(obj: A) -> Optional[ErrType]:
        return None

    assert TypedDictValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn
    ) != TypedDictValidator(
        A, overrides={"name": StringValidator()}, validate_object=obj_fn_2
    )

    class CoerceCastAsDict(Coercer[Dict[Any, Any]]):
        def __call__(self, val: Any) -> Maybe[Dict[Any, Any]]:
            try:
                return Just(dict(val))
            except (TypeError, ValueError):
                return nothing

    assert TypedDictValidator(A, coerce=None) != TypedDictValidator(
        A, coerce=CoerceCastAsDict()
    )


def test_total_is_respected() -> None:
    class TD1(TypedDict, total=False):
        a: str
        b: int
        c: float

    v = TypedDictValidator(TD1)

    assert v({}) == Valid({})

    assert v({"b": 5}) == Valid({"b": 5})

    assert v({"a": "ok", "b": 1, "c": 4.4}) == Valid({"a": "ok", "b": 1, "c": 4.4})


def test_raises_if_validate_object_and_validate_object_async() -> None:
    class Person(TypedDict):
        name: str
        age: int

    def _nobody_named_jones_is_100(
        person: Person,
    ) -> Optional[ErrType]:
        if person["name"].lower() == "jones" and person["age"] == 100:
            return SerializableErr("Cannot be jones and 100")
        else:
            return None

    async def val_obj_async(obj: Person) -> Optional[ErrType]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_is_100(obj)

    with pytest.raises(AssertionError):
        TypedDictValidator(
            Person,
            validate_object=_nobody_named_jones_is_100,
            validate_object_async=val_obj_async,
        )


@pytest.mark.asyncio
async def test_dict_validator_any_with_validate_object_async() -> None:
    cant_be_100_message = SerializableErr("jones can't be 100")

    def _nobody_named_jones_can_be_100(
        person: PersonSimpleTD,
    ) -> Optional[ErrType]:
        if person["name"].lower() == "jones" and person["age"] == 100:
            return cant_be_100_message
        else:
            return None

    async def val_obj_async(obj: PersonSimpleTD) -> Optional[ErrType]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_can_be_100(obj)

    validator = TypedDictValidator(
        PersonSimpleTD,
        validate_object_async=val_obj_async,
    )

    assert await validator.validate_async({"name": "smith", "age": 100}) == Valid(
        PersonSimpleTD(name="smith", age=100)
    )

    assert await validator.validate_async({"name": "jones", "age": 100}) == Invalid(
        cant_be_100_message, PersonSimpleTD(name="jones", age=100), validator
    )

    try:
        validator({})
    except AssertionError as e:
        assert str(e) == (
            "TypedDictValidator cannot run `validate_object_async` in synchronous calls. "
            "Please `await` the `.validate_async` method instead."
        )
    else:
        assert False


def test_coerce() -> None:
    class TryInitDict(Coercer[Dict[Any, Any]]):
        compatible_types = {List[Tuple[str, str]]}

        def __call__(self, val: Any) -> Maybe[Dict[Any, Any]]:
            try:
                return Just(dict(val))
            except (ValueError, TypeError):
                return nothing

    class X(TypedDict):
        a: str

    validator = TypedDictValidator(X, coerce=TryInitDict())
    assert validator([("a", "neat")]) == Valid({"a": "neat"})

    assert isinstance(validator([123]), Invalid)


@pytest.mark.asyncio
async def test_coerce_async() -> None:
    class TryInitDict(Coercer[Dict[Any, Any]]):
        compatible_types = {List[Tuple[str, str]]}

        def __call__(self, val: Any) -> Maybe[Dict[Any, Any]]:
            try:
                return Just(dict(val))
            except (ValueError, TypeError):
                return nothing

    class X(TypedDict):
        a: str

    validator = TypedDictValidator(X, coerce=TryInitDict())
    assert await validator.validate_async([("a", "neat")]) == Valid({"a": "neat"})

    assert isinstance(await validator.validate_async([123]), Invalid)
