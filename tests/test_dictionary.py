import asyncio
from dataclasses import dataclass
from decimal import Decimal
from re import A
from typing import Any, Dict, Hashable, List, Protocol

import pytest
from koda import Just, Maybe, nothing

from koda_validate import (
    BoolValidator,
    FloatValidator,
    IntValidator,
    ListValidator,
    MapValidator,
    MaxKeys,
    MaxLength,
    Min,
    MinKeys,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    StringValidator,
    none_validator,
    strip,
)
from koda_validate._internals import OBJECT_ERRORS_FIELD
from koda_validate.dictionary import (
    EXPECTED_MAP_ERR,
    DictValidator,
    DictValidatorAny,
    KeyNotRequired,
    is_dict_validator,
)
from koda_validate.validated import Invalid, Valid, Validated


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG: Serializable = {
    "__container__": ["can't have last_name of jones and eye color of brown"]
}


def test_is_dict() -> None:
    assert is_dict_validator({}) == Valid({})
    assert is_dict_validator(None) == Invalid(
        {"__container__": ["expected a dictionary"]}
    )
    assert is_dict_validator({"a": 1, "b": 2, 5: "whatever"}) == Valid(
        {"a": 1, "b": 2, 5: "whatever"}
    )


@pytest.mark.asyncio
async def test_is_dict_async() -> None:
    assert await is_dict_validator.validate_async({}) == Valid({})
    assert await is_dict_validator.validate_async(None) == Invalid(
        {"__container__": ["expected a dictionary"]}
    )
    assert await is_dict_validator.validate_async(
        {"a": 1, "b": 2, 5: "whatever"}
    ) == Valid({"a": 1, "b": 2, 5: "whatever"})


def test_map_validator() -> None:
    assert MapValidator(StringValidator(), FloatValidator())(None) == EXPECTED_MAP_ERR

    assert MapValidator(StringValidator(), StringValidator())(5) == Invalid(
        {"__container__": ["expected a map"]}
    )

    assert MapValidator(StringValidator(), StringValidator())({}) == Valid({})

    assert MapValidator(StringValidator(), IntValidator())({"a": 5, "b": 22}) == Valid(
        {"a": 5, "b": 22}
    )

    assert MapValidator(StringValidator(), IntValidator())({5: None}) == Invalid(
        {
            "5": {
                "key_error": ["expected a string"],
                "value_error": ["expected an integer"],
            }
        }
    )

    @dataclass(frozen=True)
    class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
        max: int

        def is_valid(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

        def err(self, val: Dict[Any, Any]) -> Serializable:
            return f"max {self.max} key(s) allowed"

    complex_validator = MapValidator(
        StringValidator(MaxLength(4)), IntValidator(Min(5)), predicates=[MaxKeys(1)]
    )
    assert complex_validator({"key1": 10, "key1a": 2},) == Invalid(
        {
            "key1a": {
                "value_error": ["minimum allowed value is 5"],
                "key_error": ["maximum allowed length is 4"],
            },
            "__container__": ["max 1 key(s) allowed"],
        }
    )

    assert complex_validator({"a": 100}) == Valid({"a": 100})

    # we need to make sure that errors are not lost even if there are key naming
    # collisions with the object field
    assert MapValidator(StringValidator(), IntValidator(), predicates=[MaxKeys(1)])(
        {OBJECT_ERRORS_FIELD: "not an int", "b": 1}
    ) == Invalid(
        {
            OBJECT_ERRORS_FIELD: [
                "max 1 key(s) allowed",
                {"value_error": ["expected an integer"]},
            ]
        }
    )

    class AddVal(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            val["newkey"] = 123
            return val

    map_validator_preprocessor = MapValidator(
        StringValidator(), IntValidator(), preprocessors=[AddVal()]
    )

    assert map_validator_preprocessor({}) == Valid({"newkey": 123})


@pytest.mark.asyncio
async def test_map_validator_async() -> None:
    assert (
        await MapValidator(StringValidator(), FloatValidator()).validate_async(None)
        == EXPECTED_MAP_ERR
    )

    assert await MapValidator(StringValidator(), StringValidator()).validate_async(
        5
    ) == Invalid({"__container__": ["expected a map"]})

    assert await MapValidator(StringValidator(), StringValidator()).validate_async(
        {}
    ) == Valid({})

    assert await MapValidator(StringValidator(), IntValidator()).validate_async(
        {"a": 5, "b": 22}
    ) == Valid({"a": 5, "b": 22})

    assert await MapValidator(StringValidator(), IntValidator()).validate_async(
        {5: None}
    ) == Invalid(
        {
            "5": {
                "key_error": ["expected a string"],
                "value_error": ["expected an integer"],
            }
        }
    )

    @dataclass(frozen=True)
    class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
        max: int

        def is_valid(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

        def err(self, val: Dict[Any, Any]) -> Serializable:
            return f"max {self.max} key(s) allowed"

    complex_validator = MapValidator(
        StringValidator(MaxLength(4)), IntValidator(Min(5)), predicates=[MaxKeys(1)]
    )
    assert await complex_validator.validate_async({"key1": 10, "key1a": 2}) == Invalid(
        {
            "key1a": {
                "value_error": ["minimum allowed value is 5"],
                "key_error": ["maximum allowed length is 4"],
            },
            "__container__": ["max 1 key(s) allowed"],
        }
    )

    assert await complex_validator.validate_async({"a": 100}) == Valid({"a": 100})

    # we need to make sure that errors are not lost even if there are key naming
    # collisions with the object field
    assert MapValidator(StringValidator(), IntValidator(), predicates=[MaxKeys(1)])(
        {OBJECT_ERRORS_FIELD: "not an int", "b": 1}
    ) == Invalid(
        {
            OBJECT_ERRORS_FIELD: [
                "max 1 key(s) allowed",
                {"value_error": ["expected an integer"]},
            ]
        }
    )

    class AddVal(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            val["newkey"] = 123
            return val

    map_validator_preprocessor = MapValidator(
        StringValidator(), IntValidator(), preprocessors=[AddVal()]
    )

    assert map_validator_preprocessor({}) == Valid({"newkey": 123})


def test_map_validator_sync_call_with_async_predicates_raises_assertion_error() -> None:
    class AsyncWait(PredicateAsync[A, Serializable]):
        async def is_valid_async(self, val: A) -> bool:
            await asyncio.sleep(0.001)
            return True

        async def err_async(self, val: A) -> Serializable:
            return "should always succeed??"

    map_validator = MapValidator(
        StringValidator(), StringValidator(), predicates_async=[AsyncWait()]
    )
    with pytest.raises(AssertionError):
        map_validator([])


def test_max_keys() -> None:
    assert MaxKeys(0)({}) == Valid({})

    assert MaxKeys(5)({"a": 1, "b": 2, "c": 3}) == Valid({"a": 1, "b": 2, "c": 3})

    assert MaxKeys(1)({"a": 1, "b": 2}) == Invalid("maximum allowed properties is 1")


def test_min_keys() -> None:
    assert MinKeys(0)({}) == Valid({})

    assert MinKeys(3)({"a": 1, "b": 2, "c": 3}) == Valid({"a": 1, "b": 2, "c": 3})

    assert MinKeys(3)({"a": 1, "b": 2}) == Invalid("minimum allowed properties is 3")


def test_obj_1() -> None:
    @dataclass
    class Person:
        name: str

    validator = DictValidator(into=Person, keys=(("name", StringValidator()),))

    assert validator("not a dict") == Invalid(
        {"__container__": ["expected a dictionary"]}
    )

    assert validator({}) == Invalid({"name": ["key missing"]})

    assert validator({"name": 5}) == Invalid({"name": ["expected a string"]})

    assert validator({"name": "bob", "age": 50}) == Invalid(
        {"__container__": ["Received unknown keys. Only expected 'name'."]}
    )

    assert validator({"name": "bob"}) == Valid(Person("bob"))


def test_obj_2() -> None:
    @dataclass
    class Person:
        name: str
        age: Maybe[int]

    validator = DictValidator(
        into=Person,
        keys=(("name", StringValidator()), ("age", KeyNotRequired(IntValidator()))),
    )

    assert validator("not a dict") == Invalid(
        {"__container__": ["expected a dictionary"]}
    )

    assert validator({}) == Invalid({"name": ["key missing"]})

    assert validator({"name": 5, "age": "50"}) == Invalid(
        {"name": ["expected a string"], "age": ["expected an integer"]}
    )

    assert validator({"name": "bob", "age": 50, "eye_color": "brown"}) == Invalid(
        {"__container__": ["Received unknown keys. Only expected 'age', 'name'."]}
    )

    assert validator({"name": "bob", "age": 50}) == Valid(Person("bob", Just(50)))
    assert validator({"name": "bob"}) == Valid(Person("bob", nothing))


def test_obj_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
        ),
    )

    assert validator({"first_name": "bob", "last_name": "smith", "age": 50}) == Valid(
        Person("bob", "smith", 50)
    )

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def _nobody_named_jones_has_brown_eyes(
    person: PersonLike,
) -> Validated[PersonLike, Serializable]:
    if person.last_name.lower() == "jones" and person.eye_color == "brown":
        return Invalid(_JONES_ERROR_MSG)
    else:
        return Valid(person)


def test_obj_4() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {"first_name": "bob", "last_name": "smith", "age": 50, "eye color": "brown"}
    ) == Valid(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", "last_name": "Jones", "age": 50, "eye color": "brown"}
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_4_mix_and_match_key_types() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            (5, StringValidator()),
            (("age", "field"), IntValidator()),
            (Decimal(6), StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {"first_name": "bob", 5: "smith", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Valid(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", 5: "Jones", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator({"bad field": 1}) == Invalid(
        {
            "__container__": [
                "Received unknown keys. Only expected "
                "'first_name', ('age', 'field'), 5, Decimal('6')."
            ]
        }
    )

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_5() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "Jones",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
        }
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_6() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
        ),
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5))

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_7() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
        ),
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8))

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_8() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float
        favorite_color: Maybe[str]

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, Just("blue")))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, nothing))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "jones",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
        }
    ) == Invalid(_JONES_ERROR_MSG)

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_9() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float
        favorite_color: Maybe[str]
        requires_none: None

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
            ("requires_none", none_validator),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
        }
    ) == Valid(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, Just("blue"), None))

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_10() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        fingers: float
        toes: float
        favorite_color: Maybe[str]
        requires_none: None
        something_else: List[str]

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", StringValidator()),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
            ("requires_none", none_validator),
            ("favorite_books", ListValidator(StringValidator())),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
        }
    ) == Valid(
        Person(
            "bob",
            "smith",
            50,
            "brown",
            True,
            6.5,
            9.8,
            Just("blue"),
            None,
            ["war and peace", "pale fire"],
        )
    )

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_obj_int_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Validated[Person, Serializable]:
        assert p.age == test_age
        assert p.name == test_name
        return Valid(p)

    dv = DictValidator(
        into=Person,
        keys=(
            (22, StringValidator()),
            (10, IntValidator()),
        ),
        validate_object=asserted_ok,
    )
    assert dv({10: test_age, 22: test_name}) == Valid(Person(test_name, test_age))


def test_obj_tuple_str_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Validated[Person, Serializable]:
        assert p.age == test_age
        assert p.name == test_name
        return Valid(p)

    dv = DictValidator(
        into=Person,
        keys=((("ok",), StringValidator()), (("neat", "cool"), IntValidator())),
        validate_object=asserted_ok,
    )
    assert dv({("ok",): test_name, ("neat", "cool"): test_age}) == Valid(
        Person(test_name, test_age)
    )


def test_obj_decimal_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Validated[Person, Serializable]:
        assert p.age == test_age
        assert p.name == test_name
        return Valid(p)

    dv = DictValidator(
        into=Person,
        keys=((Decimal(22), StringValidator()), (Decimal("1.111"), IntValidator())),
        validate_object=asserted_ok,
    )
    assert dv({Decimal("1.111"): test_age, Decimal(22): test_name}) == Valid(
        Person(test_name, test_age)
    )


def test_dict_validator_preprocessors() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    @dataclass
    class Person:
        name: str

    dv = DictValidator(
        into=Person, keys=(("name", StringValidator()),), preprocessors=[RemoveKey()]
    )

    assert dv({"a": 123, "name": "bob"}) == Valid(Person("bob"))


def test_dict_validator_any_empty() -> None:
    empty_dict_validator = DictValidatorAny(keys=())

    assert empty_dict_validator({}).val == {}

    assert empty_dict_validator({"oops": 5}).val == {
        "__container__": ["Received unknown keys. Expected empty dictionary."]
    }


def _nobody_named_jones_has_first_name_alice_dict(
    person: Dict[Hashable, Any],
) -> Validated[Dict[Hashable, Any], Serializable]:
    if person["last_name"].lower() == "jones" and person["first_name"] == Just("alice"):
        return Invalid(_JONES_ERROR_MSG)
    else:
        return Valid(person)


def test_dict_validator_any() -> None:
    validator = DictValidatorAny(
        keys=(
            ("first_name", StringValidator(preprocessors=[strip])),
            ("last_name", StringValidator()),
            ("age", IntValidator()),
            ("eye color", StringValidator()),
            ("can-fly", BoolValidator()),
            ("number_of_fingers", FloatValidator()),
            ("number of toes", FloatValidator()),
            ("favorite_color", KeyNotRequired(StringValidator())),
            ("requires_none", none_validator),
            ("favorite_books", ListValidator(StringValidator())),
            ("aaa", StringValidator()),
            ("owbwohe", IntValidator()),
            ("something else", FloatValidator()),
            (12, BoolValidator()),
        ),
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert validator(
        {
            "first_name": " bob ",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": "blue",
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
            "aaa": "bla",
            "owbwohe": 4,
            "something else": 4.4,
            12: False,
        }
    ) == Valid(
        {
            "first_name": "bob",
            "last_name": "smith",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
            "number_of_fingers": 6.5,
            "number of toes": 9.8,
            "favorite_color": Just("blue"),
            "requires_none": None,
            "favorite_books": ["war and peace", "pale fire"],
            "aaa": "bla",
            "owbwohe": 4,
            "something else": 4.4,
            12: False,
        }
    )

    assert validator("") == Invalid({"__container__": ["expected a dictionary"]})


def test_dict_validator_any_key_missing() -> None:
    validator = DictValidatorAny(
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert validator({"first_name": " bob ", "last_name": "smith"}) == Valid(
        {
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert validator({"last_name": "smith"}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert validator({"first_name": 5}) == Invalid(
        {"last_name": ["key missing"], "first_name": ["expected a string"]}
    )


def test_dict_validator_any_preprocessors() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    dv = DictValidatorAny(
        keys=(("name", StringValidator()),), preprocessors=[RemoveKey()]
    )

    assert dv({"a": 123, "name": "bob"}) == Valid({"name": "bob"})


@pytest.mark.asyncio
async def test_validate_dictionary_any_async() -> None:
    validator = DictValidatorAny(
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_first_name_alice_dict,
    )

    assert await validator.validate_async(None) == Invalid(
        {"__container__": ["expected a dictionary"]}
    )

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(
        {
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        {"last_name": ["key missing"], "first_name": ["expected a string"]}
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Invalid(
        {
            "__container__": [
                "Received unknown keys. Only expected 'first_name', 'last_name'."
            ]
        }
    )


@pytest.mark.asyncio
async def test_dict_validator_any_async_processor() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    validator = DictValidatorAny(
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        preprocessors=[RemoveKey()],
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )


@pytest.mark.asyncio
async def test_dict_validator_any_with_validate_object_async() -> None:
    async def val_obj_async(
        obj: Dict[Hashable, Any]
    ) -> Validated[Dict[Hashable, Any], Serializable]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_has_first_name_alice_dict(obj)

    validator = DictValidatorAny(
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        validate_object_async=val_obj_async,
    )

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(
        {
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        {"last_name": ["key missing"], "first_name": ["expected a string"]}
    )

    assert await validator.validate_async(
        {"last_name": "jones", "first_name": "alice"}
    ) == Invalid(_JONES_ERROR_MSG)


@pytest.mark.asyncio
async def test_dict_validator_any_no_validate_object() -> None:
    validator = DictValidatorAny(
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        )
    )
    assert await validator.validate_async(
        {"last_name": "jones", "first_name": "alice"}
    ) == Valid({"last_name": "jones", "first_name": Just("alice")})


def test_dict_validator_any_cannot_have_validate_object_and_validate_object_async() -> None:  # noqa:m E501
    async def val_obj_async(
        obj: Dict[Hashable, Any]
    ) -> Validated[Dict[Hashable, Any], Serializable]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_has_first_name_alice_dict(obj)

    with pytest.raises(AssertionError):
        DictValidatorAny(
            keys=(
                ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
                ("last_name", StringValidator()),
            ),
            validate_object=_nobody_named_jones_has_first_name_alice_dict,
            validate_object_async=val_obj_async,
        )


def test_dict_validator_cannot_have_validate_object_and_validate_object_async() -> None:  # noqa:m E501
    @dataclass
    class Person:
        name: str
        age: int

    def _nobody_named_jones_is_100(
        person: Person,
    ) -> Validated[Person, Serializable]:
        if person.name.lower() == "jones" and person.age == 100:
            return Invalid("Cannot be jones and 100")
        else:
            return Valid(person)

    async def val_obj_async(obj: Person) -> Validated[Person, Serializable]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_is_100(obj)

    with pytest.raises(AssertionError):
        DictValidator(
            into=Person,
            keys=(
                ("first_name", StringValidator(preprocessors=[strip])),
                ("age", IntValidator()),
            ),
            validate_object=_nobody_named_jones_is_100,
            validate_object_async=val_obj_async,
        )


@pytest.mark.asyncio
async def test_dict_validator_handles_validate_object_async_or_validate_object() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    def _nobody_named_jones_is_100(
        person: Person,
    ) -> Validated[Person, Serializable]:
        if person.name.lower() == "jones" and person.age == 100:
            return Invalid("Cannot be jones and 100")
        else:
            return Valid(person)

    async def val_obj_async(obj: Person) -> Validated[Person, Serializable]:
        await asyncio.sleep(0.001)
        return _nobody_named_jones_is_100(obj)

    validator_sync = DictValidator(
        into=Person,
        keys=(
            ("name", StringValidator(preprocessors=[strip])),
            ("age", IntValidator()),
        ),
        validate_object=_nobody_named_jones_is_100,
    )

    # calling sync validate_object, even within async context
    assert await validator_sync.validate_async({"name": "jones", "age": 100}) == Invalid(
        "Cannot be jones and 100"
    )

    validator_async = DictValidator(
        into=Person,
        keys=(
            ("name", StringValidator(preprocessors=[strip])),
            ("age", IntValidator()),
        ),
        validate_object_async=val_obj_async,
    )

    # calling sync validate_object_async within async context
    assert await validator_async.validate_async({"name": "jones", "age": 100}) == Invalid(
        "Cannot be jones and 100"
    )

    # calling sync validate_object_async within async context
    assert await validator_async.validate_async({"name": "other", "age": 100}) == Valid(
        Person("other", 100)
    )


@pytest.mark.asyncio
async def test_validate_dictionary_async() -> None:
    @dataclass
    class Person:
        first_name: Maybe[str]
        last_name: str

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
    )

    assert await validator.validate_async(None) == Invalid(
        {"__container__": ["expected a dictionary"]}
    )

    assert await validator.validate_async(
        {"first_name": " bob ", "last_name": "smith"}
    ) == Valid(Person(Just("bob"), "smith"))

    assert await validator.validate_async({"last_name": "smith"}) == Valid(
        Person(nothing, "smith")
    )

    assert await validator.validate_async({"first_name": 5}) == Invalid(
        {"last_name": ["key missing"], "first_name": ["expected a string"]}
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Invalid(
        {
            "__container__": [
                "Received unknown keys. Only expected 'first_name', 'last_name'."
            ]
        }
    )


@pytest.mark.asyncio
async def test_dict_validator_async_processor() -> None:
    class RemoveKey(Processor[Dict[Any, Any]]):
        def __call__(self, val: Dict[Any, Any]) -> Dict[Any, Any]:
            if "a" in val:
                del val["a"]
            return val

    @dataclass
    class Person:
        first_name: Maybe[str]
        last_name: str

    validator = DictValidator(
        into=Person,
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        preprocessors=[RemoveKey()],
    )

    assert await validator.validate_async({"last_name": "smith", "a": 123.45}) == Valid(
        Person(nothing, "smith")
    )
