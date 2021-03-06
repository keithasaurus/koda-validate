import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal as DecimalStdLib
from typing import Any, Dict, List, Protocol, Tuple

from koda.either import First, Second, Third
from koda.maybe import Just, Maybe, nothing
from koda.result import Err, Ok, Result

from koda_validate.typedefs import JSONValue, Predicate
from koda_validate.validators import (
    BLANK_STRING_MSG,
    OBJECT_ERRORS_FIELD,
    BooleanValidator,
    Choices,
    DateValidator,
    DecimalValidator,
    Dict1KeyValidator,
    Dict2KeysValidator,
    Dict3KeysValidator,
    Dict4KeysValidator,
    Dict5KeysValidator,
    Dict6KeysValidator,
    Dict7KeysValidator,
    Dict8KeysValidator,
    Dict9KeysValidator,
    Dict10KeysValidator,
    Email,
    FloatValidator,
    IntValidator,
    Lazy,
    ListValidator,
    MapValidator,
    Maximum,
    MaxItems,
    MaxKeys,
    MaxLength,
    Minimum,
    MinItems,
    MinKeys,
    MinLength,
    MultipleOf,
    NotBlank,
    Nullable,
    OneOf2,
    OneOf3,
    RegexValidator,
    StringValidator,
    Tuple2Validator,
    Tuple3Validator,
    deserialize_and_validate,
    key,
    maybe_key,
    none_validator,
    unique_items,
)


def test_float() -> None:
    assert FloatValidator()("a string") == Err(["expected a float"])

    assert FloatValidator()(5.5) == Ok(5.5)

    assert FloatValidator()(4) == Err(["expected a float"])

    assert FloatValidator(Maximum(500.0))(503.0) == Err(
        ["maximum allowed value is 500.0"]
    )

    assert FloatValidator(Maximum(500.0))(3.5) == Ok(3.5)

    assert FloatValidator(Minimum(5.0))(4.999) == Err(["minimum allowed value is 5.0"])

    assert FloatValidator(Minimum(5.0))(5.0) == Ok(5.0)

    class MustHaveAZeroSomewhere(Predicate[float, JSONValue]):
        def is_valid(self, val: float) -> bool:
            for char in str(val):
                if char == "0":
                    return True
            else:
                return False

        def err_message(self, val: float) -> JSONValue:
            return "There should be a zero in the number"

    assert FloatValidator(Minimum(2.5), Maximum(4.0), MustHaveAZeroSomewhere())(
        5.5
    ) == Err(["maximum allowed value is 4.0", "There should be a zero in the number"])


def test_decimal() -> None:
    assert DecimalValidator()("a string") == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert DecimalValidator()(5.5) == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert DecimalValidator()(DecimalStdLib("5.5")) == Ok(DecimalStdLib("5.5"))

    assert DecimalValidator()(5) == Ok(DecimalStdLib(5))

    assert DecimalValidator(Minimum(DecimalStdLib(4)), Maximum(DecimalStdLib("5.5")))(
        5
    ) == Ok(DecimalStdLib(5))


def test_boolean() -> None:
    assert BooleanValidator()("a string") == Err(["expected a boolean"])

    assert BooleanValidator()(True) == Ok(True)

    assert BooleanValidator()(False) == Ok(False)

    class RequireTrue(Predicate[bool, JSONValue]):
        def is_valid(self, val: bool) -> bool:
            return val is True

        def err_message(self, val: bool) -> JSONValue:
            return "must be true"

    assert BooleanValidator(RequireTrue())(False) == Err(["must be true"])

    assert BooleanValidator()(1) == Err(["expected a boolean"])


def test_date() -> None:
    default_date_failure = Err(["expected date formatted as yyyy-mm-dd"])
    assert DateValidator()("2021-03-21") == Ok(date(2021, 3, 21))
    assert DateValidator()("2021-3-21") == default_date_failure


def test_null() -> None:
    assert none_validator("a string") == Err(["expected null"])

    assert none_validator(None) == Ok(None)

    assert none_validator(False) == Err(["expected null"])


def test_integer() -> None:
    assert IntValidator()("a string") == Err(["expected an integer"])

    assert IntValidator()(5) == Ok(5)

    assert IntValidator()(True) == Err(["expected an integer"]), (
        "even though `bool`s are subclasses of ints in python, we wouldn't "
        "want to validate incoming data as ints if they are bools"
    )

    assert IntValidator()("5") == Err(["expected an integer"])

    assert IntValidator()(5.0) == Err(["expected an integer"])

    class DivisibleBy2(Predicate[int, JSONValue]):
        def is_valid(self, val: int) -> bool:
            return val % 2 == 0

        def err_message(self, val: int) -> JSONValue:
            return "must be divisible by 2"

    assert IntValidator(Minimum(2), Maximum(10), DivisibleBy2(),)(
        11
    ) == Err(["maximum allowed value is 10", "must be divisible by 2"])


def test_array_of() -> None:
    assert ListValidator(FloatValidator())("a string") == Err(
        {"invalid type": ["expected an array"]}
    )

    assert ListValidator(FloatValidator())([5.5, "something else"]) == Err(
        {"index 1": ["expected a float"]}
    )

    assert ListValidator(FloatValidator())([5.5, 10.1]) == Ok([5.5, 10.1])

    assert ListValidator(FloatValidator())([]) == Ok([])

    assert ListValidator(FloatValidator(Minimum(5.5)), MinItems(1), MaxItems(3))(
        [10.1, 7.7, 2.2, 5]
    ) == Err(
        {
            "index 2": ["minimum allowed value is 5.5"],
            "index 3": ["expected a float"],
            "__array__": ["maximum allowed length is 3"],
        }
    )


def test_maybe_val() -> None:
    assert Nullable(StringValidator())(None) == Ok(nothing)
    assert Nullable(StringValidator())(5) == Err(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert Nullable(StringValidator())("okok") == Ok(Just("okok"))


def test_map_of() -> None:
    assert MapValidator(StringValidator(), StringValidator())(5) == Err(
        {"invalid type": ["expected a map"]}
    )

    assert MapValidator(StringValidator(), StringValidator())({}) == Ok({})

    assert MapValidator(StringValidator(), IntValidator())({"a": 5, "b": 22}) == Ok(
        {"a": 5, "b": 22}
    )

    @dataclass(frozen=True)
    class MaxKeys(Predicate[Dict[Any, Any], JSONValue]):
        max: int

        def is_valid(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

        def err_message(self, val: Dict[Any, Any]) -> JSONValue:
            return f"max {self.max} key(s) allowed"

    complex_validator = MapValidator(
        StringValidator(MaxLength(4)), IntValidator(Minimum(5)), MaxKeys(1)
    )
    assert complex_validator({"key1": 10, "key1a": 2},) == Err(
        {
            "key1a": ["minimum allowed value is 5"],
            "key1a (key)": ["maximum allowed length is 4"],
            "__object__": ["max 1 key(s) allowed"],
        }
    )

    assert complex_validator({"a": 100}) == Ok({"a": 100})

    assert MapValidator(StringValidator(), IntValidator(), MaxKeys(1))(
        {OBJECT_ERRORS_FIELD: "not an int", "b": 1}
    ) == Err(
        {
            OBJECT_ERRORS_FIELD: [
                "max 1 key(s) allowed",
                ["expected an integer"],
            ]
        }
    ), (
        "we need to make sure that errors are not lost even if there are key naming "
        "collisions with the object field"
    )


def test_string() -> None:
    assert StringValidator()(False) == Err(["expected a string"])

    assert StringValidator()("abc") == Ok("abc")

    assert StringValidator(MaxLength(3))("something") == Err(
        ["maximum allowed length is 3"]
    )

    min_len_3_not_blank_validator = StringValidator(MinLength(3), NotBlank())

    assert min_len_3_not_blank_validator("") == Err(
        ["minimum allowed length is 3", "cannot be blank"]
    )

    assert min_len_3_not_blank_validator("   ") == Err(["cannot be blank"])

    assert min_len_3_not_blank_validator("something") == Ok("something")


def test_max_string_length() -> None:
    assert MaxLength(0)("") == Ok("")

    try:
        MaxLength(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MaxLength(5)("abc") == Ok("abc")

    assert MaxLength(5)("something") == Err("maximum allowed length is 5")


def test_min_string_length() -> None:
    assert MinLength(0)("") == Ok("")

    try:
        MinLength(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MinLength(3)("abc") == Ok("abc")

    assert MinLength(3)("zz") == Err("minimum allowed length is 3")


def test_max_items() -> None:
    assert MaxItems(0)([]) == Ok([])

    try:
        MaxItems(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MaxItems(5)([1, 2, 3]) == Ok([1, 2, 3])

    assert MaxItems(5)(["a", "b", "c", "d", "e", "fghij"]) == Err(
        "maximum allowed length is 5"
    )


def test_min_items() -> None:
    assert MinItems(0)([]) == Ok([])

    try:
        MinItems(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MinItems(3)([1, 2, 3]) == Ok([1, 2, 3])

    assert MinItems(3)([1, 2]) == Err("minimum allowed length is 3")


def test_max_properties() -> None:
    assert MaxKeys(0)({}) == Ok({})

    try:
        MaxKeys(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MaxKeys(5)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MaxKeys(1)({"a": 1, "b": 2}) == Err("maximum allowed properties is 1")


def test_min_properties() -> None:
    assert MinKeys(0)({}) == Ok({})

    try:
        MinKeys(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MinKeys(3)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MinKeys(3)({"a": 1, "b": 2}) == Err("minimum allowed properties is 3")


def test_tuple2() -> None:
    assert Tuple2Validator(StringValidator(), IntValidator())({}) == Err(
        {"invalid type": ["expected array of length 2"]}
    )

    assert Tuple2Validator(StringValidator(), IntValidator())([]) == Err(
        {"invalid type": ["expected array of length 2"]}
    )

    assert Tuple2Validator(StringValidator(), IntValidator())(["a", 1]) == Ok(("a", 1))

    assert Tuple2Validator(StringValidator(), IntValidator())([1, "a"]) == Err(
        {"index 0": ["expected a string"], "index 1": ["expected an integer"]}
    )

    def must_be_a_if_integer_is_1(
        ab: Tuple[str, int]
    ) -> Result[Tuple[str, int], JSONValue]:
        if ab[1] == 1:
            if ab[0] == "a":
                return Ok(ab)
            else:
                return Err({"__array__": ["must be a if int is 1"]})
        else:
            return Ok(ab)

    a1_validator = Tuple2Validator(
        StringValidator(), IntValidator(), must_be_a_if_integer_is_1
    )

    assert a1_validator(["a", 1]) == Ok(("a", 1))
    assert a1_validator(["b", 1]) == Err({"__array__": ["must be a if int is 1"]})
    assert a1_validator(["b", 2]) == Ok(("b", 2))


def test_tuple3() -> None:
    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        {}
    ) == Err({"invalid type": ["expected array of length 3"]})

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        []
    ) == Err({"invalid type": ["expected array of length 3"]})

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        ["a", 1, False]
    ) == Ok(("a", 1, False))

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        [1, "a", 7.42]
    ) == Err(
        {
            "index 0": ["expected a string"],
            "index 1": ["expected an integer"],
            "index 2": ["expected a boolean"],
        }
    )

    def must_be_a_if_1_and_true(
        abc: Tuple[str, int, bool]
    ) -> Result[Tuple[str, int, bool], JSONValue]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return Ok(abc)
            else:
                return Err({"__array__": ["must be a if int is 1 and bool is True"]})
        else:
            return Ok(abc)

    a1_validator = Tuple3Validator(
        StringValidator(), IntValidator(), BooleanValidator(), must_be_a_if_1_and_true
    )

    assert a1_validator(["a", 1, True]) == Ok(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Err(
        {"__array__": ["must be a if int is 1 and bool is True"]}
    )
    assert a1_validator(["b", 2, False]) == Ok(("b", 2, False))


def test_obj_1() -> None:
    @dataclass
    class Person:
        name: str

    validator = Dict1KeyValidator(key("name", StringValidator()), into=Person)

    assert validator("not a dict") == Err({"__object__": ["expected an object"]})

    assert validator({}) == Err({"name": ["key missing"]})

    assert validator({"name": 5}) == Err({"name": ["expected a string"]})

    assert validator({"name": "bob", "age": 50}) == Err(
        {"__object__": ["Received unknown keys. Only expected ['name']"]}
    )

    assert validator({"name": "bob"}) == Ok(Person("bob"))


def test_obj_2() -> None:
    @dataclass
    class Person:
        name: str
        age: Maybe[int]

    validator = Dict2KeysValidator(
        key("name", StringValidator()), maybe_key("age", IntValidator()), into=Person
    )

    assert validator("not a dict") == Err({"__object__": ["expected an object"]})

    assert validator({}) == Err({"name": ["key missing"]})

    assert validator({"name": 5, "age": "50"}) == Err(
        {"name": ["expected a string"], "age": ["expected an integer"]}
    )

    assert validator({"name": "bob", "age": 50, "eye_color": "brown"}) == Err(
        {"__object__": ["Received unknown keys. Only expected ['age', 'name']"]}
    )

    assert validator({"name": "bob", "age": 50}) == Ok(Person("bob", Just(50)))
    assert validator({"name": "bob"}) == Ok(Person("bob", nothing))


def test_obj_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    validator = Dict3KeysValidator(
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        into=Person,
    )

    assert validator({"first_name": "bob", "last_name": "smith", "age": 50}) == Ok(
        Person("bob", "smith", 50)
    )

    assert validator("") == Err({"__object__": ["expected an object"]})


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG: JSONValue = {
    "__object__": ["can't have last_name of jones and eye color of brown"]
}


def _nobody_named_jones_has_brown_eyes(
    person: PersonLike,
) -> Result[PersonLike, JSONValue]:
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
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        into=Person,
        validate_object=_nobody_named_jones_has_brown_eyes,
    )

    assert validator(
        {"first_name": "bob", "last_name": "smith", "age": 50, "eye color": "brown"}
    ) == Ok(Person("bob", "smith", 50, "brown"))

    assert validator(
        {"first_name": "bob", "last_name": "Jones", "age": 50, "eye color": "brown"}
    ) == Err(_JONES_ERROR_MSG)

    assert validator("") == Err({"__object__": ["expected an object"]})


def test_obj_5() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool

    validator = Dict5KeysValidator(
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        into=Person,
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

    assert validator("") == Err({"__object__": ["expected an object"]})


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
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        into=Person,
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

    assert validator("") == Err({"__object__": ["expected an object"]})


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
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
        into=Person,
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

    assert validator("") == Err({"__object__": ["expected an object"]})


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
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
        maybe_key("favorite_color", StringValidator()),
        into=Person,
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

    assert validator("") == Err({"__object__": ["expected an object"]})


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
        key("first_name", StringValidator()),
        key("last_name", StringValidator()),
        key("age", IntValidator()),
        key("eye color", StringValidator()),
        key("can-fly", BooleanValidator()),
        key("number_of_fingers", FloatValidator()),
        key("number of toes", FloatValidator()),
        maybe_key("favorite_color", StringValidator()),
        key("requires_none", none_validator),
        into=Person,
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

    assert validator("") == Err({"__object__": ["expected an object"]})


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
        into=Person,
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

    assert validator("") == Err({"__object__": ["expected an object"]})


def test_choices() -> None:
    validator = Choices({"a", "bc", "def"})

    assert validator("bc") == Ok("bc")
    assert validator("not present") == Err("expected one of ['a', 'bc', 'def']")


def test_not_blank() -> None:
    assert NotBlank()("a") == Ok("a")
    assert NotBlank()("") == Err(BLANK_STRING_MSG)
    assert NotBlank()(" ") == Err(BLANK_STRING_MSG)
    assert NotBlank()("\t") == Err(BLANK_STRING_MSG)
    assert NotBlank()("\n") == Err(BLANK_STRING_MSG)


def test_first_of2() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert str_or_int_validator("ok") == Ok(First("ok"))
    assert str_or_int_validator(5) == Ok(Second(5))
    assert str_or_int_validator(5.5) == Err(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )

    str_or_int_validator_named = OneOf2(
        ("name", StringValidator()), ("age", IntValidator())
    )

    assert str_or_int_validator_named(5.5) == Err(
        {"name": ["expected a string"], "age": ["expected an integer"]}
    )


def test_first_of3() -> None:
    str_or_int_or_float_validator = OneOf3(
        StringValidator(), IntValidator(), FloatValidator()
    )
    assert str_or_int_or_float_validator("ok") == Ok(First("ok"))
    assert str_or_int_or_float_validator(5) == Ok(Second(5))
    assert str_or_int_or_float_validator(5.5) == Ok(Third(5.5))
    assert str_or_int_or_float_validator(True) == Err(
        {
            "variant 1": ["expected a string"],
            "variant 2": ["expected an integer"],
            "variant 3": ["expected a float"],
        }
    )

    str_or_int_validator_named = OneOf3(
        ("name", StringValidator()),
        ("age", IntValidator()),
        ("alive", FloatValidator()),
    )

    assert str_or_int_validator_named(False) == Err(
        {
            "name": ["expected a string"],
            "age": ["expected an integer"],
            "alive": ["expected a float"],
        }
    )


def test_email() -> None:
    assert Email()("notanemail") == Err("expected a valid email address")
    assert Email()("a@b.com") == Ok("a@b.com")

    custom_regex_validator = Email(re.compile(r"[a-z.]+@somecompany\.com"))
    assert custom_regex_validator("a.b@somecompany.com") == Ok("a.b@somecompany.com")
    assert custom_regex_validator("a.b@example.com") == Err(
        "expected a valid email address"
    )


def deserialize_and_validate_tests() -> None:
    @dataclass
    class Person:
        name: str
        age: int

    validator = Dict2KeysValidator(
        key("name", StringValidator()), key("int", IntValidator()), into=Person
    )

    assert deserialize_and_validate(validator, "") == Err(
        {"invalid type": ["expected an object"]}
    )

    assert deserialize_and_validate(validator, "[") == Err({"bad data": "invalid json"})

    assert deserialize_and_validate(validator, '{"name": "Bob", "age": 100}') == Ok(
        Person("Bob", 100)
    )


def test_lazy() -> None:
    @dataclass
    class TestNonEmptyList:
        val: int
        next: Maybe["TestNonEmptyList"]  # noqa: F821

    def recur_tnel() -> Dict2KeysValidator[
        int, Maybe[TestNonEmptyList], TestNonEmptyList
    ]:
        return nel_validator

    nel_validator: Dict2KeysValidator[
        int, Maybe[TestNonEmptyList], TestNonEmptyList
    ] = Dict2KeysValidator(
        key("val", IntValidator()),
        maybe_key("next", Lazy(recur_tnel)),
        into=TestNonEmptyList,
    )

    assert nel_validator({"val": 5, "next": {"val": 6, "next": {"val": 7}}}) == Ok(
        TestNonEmptyList(5, Just(TestNonEmptyList(6, Just(TestNonEmptyList(7, nothing)))))
    )


def test_unique_items() -> None:
    unique_fail = Err("all items must be unique")
    assert unique_items([1, 2, 3]) == Ok([1, 2, 3])
    assert unique_items([1, 1]) == unique_fail
    assert unique_items([1, [], []]) == unique_fail
    assert unique_items([[], [1], [2]]) == Ok([[], [1], [2]])
    assert unique_items([{"something": {"a": 1}}, {"something": {"a": 1}}]) == unique_fail


def test_regex_validator() -> None:
    assert RegexValidator(re.compile(r".+"))("something") == Ok("something")
    assert RegexValidator(re.compile(r".+"))("") == Err("must match pattern .+")


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) == Ok(10)
    assert MultipleOf(5)(11) == Err("expected multiple of 5")
    assert MultipleOf(2.2)(4.40) == Ok(4.40)
