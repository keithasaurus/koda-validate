from dataclasses import dataclass
from typing import Any, Dict, List

from koda import Err, Just, Maybe, Ok, Result, nothing

from koda_validate import (
    BooleanValidator,
    FloatValidator,
    IntValidator,
    ListValidator,
    MapValidator,
    MaxKeys,
    MaxLength,
    Min,
    MinKeys,
    Predicate,
    Serializable,
    StringValidator,
    dict_validator,
    key,
    maybe_key,
    none_validator,
)
from koda_validate.dictionary import (
    Dict4KeysValidator,
    Dict5KeysValidator,
    Dict6KeysValidator,
    Dict7KeysValidator,
    Dict8KeysValidator,
    Dict9KeysValidator,
    Dict10KeysValidator,
    is_dict_validator,
)
from koda_validate.utils import OBJECT_ERRORS_FIELD
from tests.test_validators import _JONES_ERROR_MSG, PersonLike


def test_is_dict() -> None:
    assert is_dict_validator({}) == Ok({})
    assert is_dict_validator(None) == Err({"__container__": ["expected a dictionary"]})
    assert is_dict_validator({"a": 1, "b": 2, 5: "whatever"}) == Ok(
        {"a": 1, "b": 2, 5: "whatever"}
    )


def test_map_validator() -> None:
    assert MapValidator(StringValidator(), StringValidator())(5) == Err(
        {"__container__": ["expected a map"]}
    )

    assert MapValidator(StringValidator(), StringValidator())({}) == Ok({})

    assert MapValidator(StringValidator(), IntValidator())({"a": 5, "b": 22}) == Ok(
        {"a": 5, "b": 22}
    )

    @dataclass(frozen=True)
    class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
        max: int

        def is_valid(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

        def err_output(self, val: Dict[Any, Any]) -> Serializable:
            return f"max {self.max} key(s) allowed"

    complex_validator = MapValidator(
        StringValidator(MaxLength(4)), IntValidator(Min(5)), MaxKeys(1)
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

    assert MapValidator(StringValidator(), IntValidator(), MaxKeys(1))(
        {OBJECT_ERRORS_FIELD: "not an int", "b": 1}
    ) == Err(
        {
            OBJECT_ERRORS_FIELD: [
                "max 1 key(s) allowed",
                {"value_error": ["expected an integer"]},
            ]
        }
    ), (
        "we need to make sure that errors are not lost even if there are key naming "
        "collisions with the object field"
    )


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

    validator = dict_validator(Person, key("name", StringValidator()))

    assert validator("not a dict") == Err({"__container__": ["expected a dictionary"]})

    assert validator({}) == Err({"name": ["key missing"]})

    assert validator({"name": 5}) == Err({"name": ["expected a string"]})

    assert validator({"name": "bob", "age": 50}) == Err(
        {"__container__": ["Received unknown keys. Only expected ['name']"]}
    )

    assert validator({"name": "bob"}) == Ok(Person("bob"))


def test_obj_2() -> None:
    @dataclass
    class Person:
        name: str
        age: Maybe[int]

    validator = dict_validator(
        Person, key("name", StringValidator()), maybe_key("age", IntValidator())
    )

    assert validator("not a dict") == Err({"__container__": ["expected a dictionary"]})

    assert validator({}) == Err({"name": ["key missing"]})

    assert validator({"name": 5, "age": "50"}) == Err(
        {"name": ["expected a string"], "age": ["expected an integer"]}
    )

    assert validator({"name": "bob", "age": 50, "eye_color": "brown"}) == Err(
        {"__container__": ["Received unknown keys. Only expected ['age', 'name']"]}
    )

    assert validator({"name": "bob", "age": 50}) == Ok(Person("bob", Just(50)))
    assert validator({"name": "bob"}) == Ok(Person("bob", nothing))


def test_obj_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    validator = dict_validator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
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

    validator = Dict4KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {"first_name": "bob", "last_name": "smith", "age": 50, "eye color": "brown"}
    ) == Ok(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", "last_name": "Jones", "age": 50, "eye color": "brown"}
    ) == Err(_JONES_ERROR_MSG)

    assert validator("") == Err({"__container__": ["expected a dictionary"]})


def test_obj_5() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool

    validator = Dict5KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
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

    validator = Dict6KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
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

    validator = Dict7KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
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

    validator = Dict8KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
        maybe_key("favorite_color", StringValidator()),
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

    validator = Dict9KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
        maybe_key("favorite_color", StringValidator()),
        key("requires_none", none_validator),
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

    validator = Dict10KeysValidator(
        Person,
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
        maybe_key("favorite_color", StringValidator()),
        key("requires_none", none_validator),
        key("favorite_books", ListValidator(StringValidator())),
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
