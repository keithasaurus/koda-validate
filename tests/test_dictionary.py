from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Hashable, List, Protocol

import pytest
from koda import Err, Just, Maybe, Ok, Result, nothing

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
    Processor,
    Serializable,
    StringValidator,
    none_validator,
    strip,
)
from koda_validate.dictionary import (
    EXPECTED_MAP_ERR,
    DictValidator,
    DictValidatorAny,
    KeyNotRequired,
    is_dict_validator,
)
from koda_validate.utils import OBJECT_ERRORS_FIELD


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG: Serializable = {
    "__container__": ["can't have last_name of jones and eye color of brown"]
}


def test_is_dict() -> None:
    assert is_dict_validator({}) == Ok({})
    assert is_dict_validator(None) == Err({"__container__": ["expected a dictionary"]})
    assert is_dict_validator({"a": 1, "b": 2, 5: "whatever"}) == Ok(
        {"a": 1, "b": 2, 5: "whatever"}
    )


@pytest.mark.asyncio
async def test_is_dict_async() -> None:
    assert await is_dict_validator.validate_async({}) == Ok({})
    assert await is_dict_validator.validate_async(None) == Err(
        {"__container__": ["expected a dictionary"]}
    )
    assert await is_dict_validator.validate_async({"a": 1, "b": 2, 5: "whatever"}) == Ok(
        {"a": 1, "b": 2, 5: "whatever"}
    )


def test_map_validator() -> None:
    assert MapValidator(StringValidator(), FloatValidator())(None) == EXPECTED_MAP_ERR

    assert MapValidator(StringValidator(), StringValidator())(5) == Err(
        {"__container__": ["expected a map"]}
    )

    assert MapValidator(StringValidator(), StringValidator())({}) == Ok({})

    assert MapValidator(StringValidator(), IntValidator())({"a": 5, "b": 22}) == Ok(
        {"a": 5, "b": 22}
    )

    assert MapValidator(StringValidator(), IntValidator())({5: None}) == Err(
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
    assert complex_validator({"key1": 10, "key1a": 2},) == Err(
        {
            "key1a": {
                "value_error": ["minimum allowed value is 5"],
                "key_error": ["maximum allowed length is 4"],
            },
            "__container__": ["max 1 key(s) allowed"],
        }
    )

    assert complex_validator({"a": 100}) == Ok({"a": 100})

    # we need to make sure that errors are not lost even if there are key naming
    # collisions with the object field
    assert MapValidator(StringValidator(), IntValidator(), predicates=[MaxKeys(1)])(
        {OBJECT_ERRORS_FIELD: "not an int", "b": 1}
    ) == Err(
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

    assert map_validator_preprocessor({}) == Ok({"newkey": 123})


@pytest.mark.asyncio
async def test_map_validator_async() -> None:
    assert (
        await MapValidator(StringValidator(), FloatValidator()).validate_async(None)
        == EXPECTED_MAP_ERR
    )

    assert await MapValidator(StringValidator(), StringValidator()).validate_async(
        5
    ) == Err({"__container__": ["expected a map"]})

    assert await MapValidator(StringValidator(), StringValidator()).validate_async(
        {}
    ) == Ok({})

    assert await MapValidator(StringValidator(), IntValidator()).validate_async(
        {"a": 5, "b": 22}
    ) == Ok({"a": 5, "b": 22})

    assert await MapValidator(StringValidator(), IntValidator()).validate_async(
        {5: None}
    ) == Err(
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
    assert await complex_validator.validate_async({"key1": 10, "key1a": 2}) == Err(
        {
            "key1a": {
                "value_error": ["minimum allowed value is 5"],
                "key_error": ["maximum allowed length is 4"],
            },
            "__container__": ["max 1 key(s) allowed"],
        }
    )

    assert await complex_validator.validate_async({"a": 100}) == Ok({"a": 100})

    # we need to make sure that errors are not lost even if there are key naming
    # collisions with the object field
    assert MapValidator(StringValidator(), IntValidator(), predicates=[MaxKeys(1)])(
        {OBJECT_ERRORS_FIELD: "not an int", "b": 1}
    ) == Err(
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

    assert map_validator_preprocessor({}) == Ok({"newkey": 123})


def test_max_keys() -> None:
    assert MaxKeys(0)({}) == Ok({})

    assert MaxKeys(5)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MaxKeys(1)({"a": 1, "b": 2}) == Err("maximum allowed properties is 1")


def test_min_keys() -> None:
    assert MinKeys(0)({}) == Ok({})

    assert MinKeys(3)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MinKeys(3)({"a": 1, "b": 2}) == Err("minimum allowed properties is 3")


def test_obj_1() -> None:
    @dataclass
    class Person:
        name: str

    validator = DictValidator(into=Person, keys=(("name", StringValidator()),))

    assert validator("not a dict") == Err({"__container__": ["expected a dictionary"]})

    assert validator({}) == Err({"name": ["key missing"]})

    assert validator({"name": 5}) == Err({"name": ["expected a string"]})

    assert validator({"name": "bob", "age": 50}) == Err(
        {"__container__": ["Received unknown keys. Only expected 'name'."]}
    )

    assert validator({"name": "bob"}) == Ok(Person("bob"))


def test_obj_2() -> None:
    @dataclass
    class Person:
        name: str
        age: Maybe[int]

    validator = DictValidator(
        into=Person,
        keys=(("name", StringValidator()), ("age", KeyNotRequired(IntValidator()))),
    )

    assert validator("not a dict") == Err({"__container__": ["expected a dictionary"]})

    assert validator({}) == Err({"name": ["key missing"]})

    assert validator({"name": 5, "age": "50"}) == Err(
        {"name": ["expected a string"], "age": ["expected an integer"]}
    )

    assert validator({"name": "bob", "age": 50, "eye_color": "brown"}) == Err(
        {"__container__": ["Received unknown keys. Only expected 'age', 'name'."]}
    )

    assert validator({"name": "bob", "age": 50}) == Ok(Person("bob", Just(50)))
    assert validator({"name": "bob"}) == Ok(Person("bob", nothing))


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

    assert validator({"first_name": "bob", "last_name": "smith", "age": 50}) == Ok(
        Person("bob", "smith", 50)
    )

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


def _nobody_named_jones_has_brown_eyes(
    person: PersonLike,
) -> Result[PersonLike, Serializable]:
    if person.last_name.lower() == "jones" and person.eye_color == "brown":
        return Err(_JONES_ERROR_MSG)
    else:
        return Ok(person)


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
    ) == Ok(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", "last_name": "Jones", "age": 50, "eye color": "brown"}
    ) == Err(_JONES_ERROR_MSG)

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", 5: "Jones", ("age", "field"): 50, Decimal(6): "brown"}
    ) == Err(_JONES_ERROR_MSG)

    assert validator({"bad field": 1}) == Err(
        {
            "__container__": [
                "Received unknown keys. Only expected "
                "'first_name', ('age', 'field'), 5, Decimal('6')."
            ]
        }
    )

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(Person("bob", "smith", 50, "brown", True))

    assert validator(
        {
            "first_name": "bob",
            "last_name": "Jones",
            "age": 50,
            "eye color": "brown",
            "can-fly": True,
        }
    ) == Err(_JONES_ERROR_MSG)

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(Person("bob", "smith", 50, "brown", True, 6.5))

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(Person("bob", "smith", 50, "brown", True, 6.5, 9.8))

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, Just("blue")))

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
    ) == Ok(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, nothing))

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
    ) == Err(_JONES_ERROR_MSG)

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(Person("bob", "smith", 50, "brown", True, 6.5, 9.8, Just("blue"), None))

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


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
    ) == Ok(
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

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


def test_obj_int_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Result[Person, Serializable]:
        assert p.age == test_age
        assert p.name == test_name
        return Ok(p)

    dv = DictValidator(
        into=Person,
        keys=(
            (22, StringValidator()),
            (10, IntValidator()),
        ),
        validate_object=asserted_ok,
    )
    assert dv({10: test_age, 22: test_name}) == Ok(Person(test_name, test_age))


def test_obj_tuple_str_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Result[Person, Serializable]:
        assert p.age == test_age
        assert p.name == test_name
        return Ok(p)

    dv = DictValidator(
        into=Person,
        keys=((("ok",), StringValidator()), (("neat", "cool"), IntValidator())),
        validate_object=asserted_ok,
    )
    assert dv({("ok",): test_name, ("neat", "cool"): test_age}) == Ok(
        Person(test_name, test_age)
    )


def test_obj_decimal_keys() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    test_age = 10
    test_name = "bob"

    def asserted_ok(p: Person) -> Result[Person, Serializable]:
        assert p.age == test_age
        assert p.name == test_name
        return Ok(p)

    dv = DictValidator(
        into=Person,
        keys=((Decimal(22), StringValidator()), (Decimal("1.111"), IntValidator())),
        validate_object=asserted_ok,
    )
    assert dv({Decimal("1.111"): test_age, Decimal(22): test_name}) == Ok(
        Person(test_name, test_age)
    )


def test_dict_validator_unsafe_empty() -> None:
    empty_dict_validator = DictValidatorAny(keys=())

    assert empty_dict_validator({}).val == {}

    assert empty_dict_validator({"oops": 5}).val == {
        "__container__": ["Received unknown keys. Expected empty dictionary."]
    }


def _nobody_named_jones_has_brown_eyes_dict_any(
    person: Dict[Hashable, Any],
) -> Result[Dict[Hashable, Any], Serializable]:
    if person["last_name"].lower() == "jones" and person["eye_color"] == "brown":
        return Err(_JONES_ERROR_MSG)
    else:
        return Ok(person)


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
        validate_object=_nobody_named_jones_has_brown_eyes_dict_any,
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
    ) == Ok(
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

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


def test_dict_validator_any_key_missing() -> None:
    validator = DictValidatorAny(
        keys=(
            ("first_name", KeyNotRequired(StringValidator(preprocessors=[strip]))),
            ("last_name", StringValidator()),
        ),
        validate_object=_nobody_named_jones_has_brown_eyes_dict_any,
    )

    assert validator({"first_name": " bob ", "last_name": "smith",}) == Ok(
        {
            "first_name": Just("bob"),
            "last_name": "smith",
        }
    )

    assert validator({"last_name": "smith"}) == Ok(
        {"first_name": nothing, "last_name": "smith"}
    )

    assert validator({"first_name": 5}) == Err(
        {"last_name": ["key missing"], "first_name": ["expected a string"]}
    )
