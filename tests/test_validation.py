import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal as DecimalStdLib
from typing import Any, Dict, List, Protocol, Tuple

from koda.either import First, Second, Third
from koda.maybe import Just, Maybe, nothing
from koda.result import Err, Ok, Result

from koda_validate.typedefs import Jsonish, PredicateValidator
from koda_validate.validation import (
    BLANK_STRING_MSG,
    OBJECT_ERRORS_FIELD,
    ArrayOf,
    Boolean,
    Date,
    Decimal,
    Email,
    Enum,
    Float,
    Integer,
    Lazy,
    MapOf,
    Maximum,
    MaxItems,
    MaxLength,
    MaxProperties,
    Minimum,
    MinItems,
    MinLength,
    MinProperties,
    MultipleOf,
    NotBlank,
    Null,
    Nullable,
    Obj1Prop,
    Obj2Props,
    Obj3Props,
    Obj4Props,
    Obj5Props,
    Obj6Props,
    Obj7Props,
    Obj8Props,
    Obj9Props,
    Obj10Props,
    OneOf2,
    OneOf3,
    RegexValidator,
    String,
    Tuple2,
    Tuple3,
    deserialize_and_validate,
    maybe_prop,
    prop,
    unique_items,
)


def test_float() -> None:
    assert Float()("a string") == Err(["expected a float"])

    assert Float()(5.5) == Ok(5.5)

    assert Float()(4) == Err(["expected a float"])

    assert Float(Maximum(500.0))(503.0) == Err(["maximum allowed value is 500.0"])

    assert Float(Maximum(500.0))(3.5) == Ok(3.5)

    assert Float(Minimum(5.0))(4.999) == Err(["minimum allowed value is 5.0"])

    assert Float(Minimum(5.0))(5.0) == Ok(5.0)

    class MustHaveAZeroSomewhere(PredicateValidator[float, Jsonish]):
        def is_valid(self, val: float) -> bool:
            for char in str(val):
                if char == "0":
                    return True
            else:
                return False

        def err_message(self, val: float) -> Jsonish:
            return "There should be a zero in the number"

    assert Float(Minimum(2.5), Maximum(4.0), MustHaveAZeroSomewhere())(5.5) == Err(
        ["maximum allowed value is 4.0", "There should be a zero in the number"]
    )


def test_decimal() -> None:
    assert Decimal()("a string") == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert Decimal()(5.5) == Err(["expected a decimal-compatible string or integer"])

    assert Decimal()(DecimalStdLib("5.5")) == Ok(DecimalStdLib("5.5"))

    assert Decimal()(5) == Ok(DecimalStdLib(5))

    assert Decimal(Minimum(DecimalStdLib(4)), Maximum(DecimalStdLib("5.5")))(5) == Ok(
        DecimalStdLib(5)
    )


def test_boolean() -> None:
    assert Boolean()("a string") == Err(["expected a boolean"])

    assert Boolean()(True) == Ok(True)

    assert Boolean()(False) == Ok(False)

    class RequireTrue(PredicateValidator[bool, Jsonish]):
        def is_valid(self, val: bool) -> bool:
            return val is True

        def err_message(self, val: bool) -> Jsonish:
            return "must be true"

    assert Boolean(RequireTrue())(False) == Err(["must be true"])

    assert Boolean()(1) == Err(["expected a boolean"])


def test_date() -> None:
    default_date_failure = Err(["expected date formatted as yyyy-mm-dd"])
    assert Date()("2021-03-21") == Ok(date(2021, 3, 21))
    assert Date()("2021-3-21") == default_date_failure


def test_null() -> None:
    assert Null("a string") == Err(["expected null"])

    assert Null(None) == Ok(None)

    assert Null(False) == Err(["expected null"])


def test_integer() -> None:
    assert Integer()("a string") == Err(["expected an integer"])

    assert Integer()(5) == Ok(5)

    assert Integer()(True) == Err(["expected an integer"]), (
        "even though `bool`s are subclasses of ints in python, we wouldn't "
        "want to validate incoming data as ints if they are bools"
    )

    assert Integer()("5") == Err(["expected an integer"])

    assert Integer()(5.0) == Err(["expected an integer"])

    class DivisibleBy2(PredicateValidator[int, Jsonish]):
        def is_valid(self, val: int) -> bool:
            return val % 2 == 0

        def err_message(self, val: int) -> Jsonish:
            return "must be divisible by 2"

    assert Integer(Minimum(2), Maximum(10), DivisibleBy2(),)(
        11
    ) == Err(["maximum allowed value is 10", "must be divisible by 2"])


def test_array_of() -> None:
    assert ArrayOf(Float())("a string") == Err({"invalid type": ["expected an array"]})

    assert ArrayOf(Float())([5.5, "something else"]) == Err(
        {"index 1": ["expected a float"]}
    )

    assert ArrayOf(Float())([5.5, 10.1]) == Ok([5.5, 10.1])

    assert ArrayOf(Float())([]) == Ok([])

    assert ArrayOf(Float(Minimum(5.5)), MinItems(1), MaxItems(3))(
        [10.1, 7.7, 2.2, 5]
    ) == Err(
        {
            "index 2": ["minimum allowed value is 5.5"],
            "index 3": ["expected a float"],
            "__array__": ["maximum allowed length is 3"],
        }
    )


def test_maybe_val() -> None:
    assert Nullable(String())(None) == Ok(nothing)
    assert Nullable(String())(5) == Err(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert Nullable(String())("okok") == Ok(Just("okok"))


def test_map_of() -> None:
    assert MapOf(String(), String())(5) == Err({"invalid type": ["expected a map"]})

    assert MapOf(String(), String())({}) == Ok({})

    assert MapOf(String(), Integer())({"a": 5, "b": 22}) == Ok({"a": 5, "b": 22})

    @dataclass(frozen=True)
    class MaxKeys(PredicateValidator[Dict[Any, Any], Jsonish]):
        max: int

        def is_valid(self, val: Dict[Any, Any]) -> bool:
            return len(val) <= self.max

        def err_message(self, val: Dict[Any, Any]) -> Jsonish:
            return f"max {self.max} key(s) allowed"

    complex_validator = MapOf(String(MaxLength(4)), Integer(Minimum(5)), MaxKeys(1))
    assert complex_validator({"key1": 10, "key1a": 2},) == Err(
        {
            "key1a": ["minimum allowed value is 5"],
            "key1a (key)": ["maximum allowed length is 4"],
            "__object__": ["max 1 key(s) allowed"],
        }
    )

    assert complex_validator({"a": 100}) == Ok({"a": 100})

    assert MapOf(String(), Integer(), MaxKeys(1))(
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
    assert String()(False) == Err(["expected a string"])

    assert String()("abc") == Ok("abc")

    assert String(MaxLength(3))("something") == Err(["maximum allowed length is 3"])

    min_len_3_not_blank_validator = String(MinLength(3), NotBlank())

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
    assert MaxProperties(0)({}) == Ok({})

    try:
        MaxProperties(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MaxProperties(5)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MaxProperties(1)({"a": 1, "b": 2}) == Err("maximum allowed properties is 1")


def test_min_properties() -> None:
    assert MinProperties(0)({}) == Ok({})

    try:
        MinProperties(-1)
    except AssertionError:
        pass
    else:
        raise AssertionError("should have raised error in try call")

    assert MinProperties(3)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MinProperties(3)({"a": 1, "b": 2}) == Err("minimum allowed properties is 3")


def test_tuple2() -> None:
    assert Tuple2(String(), Integer())({}) == Err(
        {"invalid type": ["expected array of length 2"]}
    )

    assert Tuple2(String(), Integer())([]) == Err(
        {"invalid type": ["expected array of length 2"]}
    )

    assert Tuple2(String(), Integer())(["a", 1]) == Ok(("a", 1))

    assert Tuple2(String(), Integer())([1, "a"]) == Err(
        {"index 0": ["expected a string"], "index 1": ["expected an integer"]}
    )

    def must_be_a_if_integer_is_1(
        ab: Tuple[str, int]
    ) -> Result[Tuple[str, int], Jsonish]:
        if ab[1] == 1:
            if ab[0] == "a":
                return Ok(ab)
            else:
                return Err({"__array__": ["must be a if int is 1"]})
        else:
            return Ok(ab)

    a1_validator = Tuple2(String(), Integer(), must_be_a_if_integer_is_1)

    assert a1_validator(["a", 1]) == Ok(("a", 1))
    assert a1_validator(["b", 1]) == Err({"__array__": ["must be a if int is 1"]})
    assert a1_validator(["b", 2]) == Ok(("b", 2))


def test_tuple3() -> None:
    assert Tuple3(String(), Integer(), Boolean())({}) == Err(
        {"invalid type": ["expected array of length 3"]}
    )

    assert Tuple3(String(), Integer(), Boolean())([]) == Err(
        {"invalid type": ["expected array of length 3"]}
    )

    assert Tuple3(String(), Integer(), Boolean())(["a", 1, False]) == Ok(("a", 1, False))

    assert Tuple3(String(), Integer(), Boolean())([1, "a", 7.42]) == Err(
        {
            "index 0": ["expected a string"],
            "index 1": ["expected an integer"],
            "index 2": ["expected a boolean"],
        }
    )

    def must_be_a_if_1_and_true(
        abc: Tuple[str, int, bool]
    ) -> Result[Tuple[str, int, bool], Jsonish]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return Ok(abc)
            else:
                return Err({"__array__": ["must be a if int is 1 and bool is True"]})
        else:
            return Ok(abc)

    a1_validator = Tuple3(String(), Integer(), Boolean(), must_be_a_if_1_and_true)

    assert a1_validator(["a", 1, True]) == Ok(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Err(
        {"__array__": ["must be a if int is 1 and bool is True"]}
    )
    assert a1_validator(["b", 2, False]) == Ok(("b", 2, False))


def test_obj_1() -> None:
    @dataclass
    class Person:
        name: str

    validator = Obj1Prop(prop("name", String()), into=Person)

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

    validator = Obj2Props(
        prop("name", String()), maybe_prop("age", Integer()), into=Person
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

    validator = Obj3Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        into=Person,
    )

    assert validator({"first_name": "bob", "last_name": "smith", "age": 50}) == Ok(
        Person("bob", "smith", 50)
    )

    assert validator("") == Err({"__object__": ["expected an object"]})


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG: Jsonish = {
    "__object__": ["can't have last_name of jones and eye color of brown"]
}


def _nobody_named_jones_has_brown_eyes(
    person: PersonLike,
) -> Result[PersonLike, Jsonish]:
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

    validator = Obj4Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
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

    validator = Obj5Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
        prop("can-fly", Boolean()),
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

    validator = Obj6Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
        prop("can-fly", Boolean()),
        prop("number_of_fingers", Float()),
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

    validator = Obj7Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
        prop("can-fly", Boolean()),
        prop("number_of_fingers", Float()),
        prop("number of toes", Float()),
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

    validator = Obj8Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
        prop("can-fly", Boolean()),
        prop("number_of_fingers", Float()),
        prop("number of toes", Float()),
        maybe_prop("favorite_color", String()),
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

    validator = Obj9Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
        prop("can-fly", Boolean()),
        prop("number_of_fingers", Float()),
        prop("number of toes", Float()),
        maybe_prop("favorite_color", String()),
        prop("requires_none", Null),
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

    validator = Obj10Props(
        prop("first_name", String()),
        prop("last_name", String()),
        prop("age", Integer()),
        prop("eye color", String()),
        prop("can-fly", Boolean()),
        prop("number_of_fingers", Float()),
        prop("number of toes", Float()),
        maybe_prop("favorite_color", String()),
        prop("requires_none", Null),
        prop("favorite_books", ArrayOf(String())),
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
    validator = Enum({"a", "bc", "def"})

    assert validator("bc") == Ok("bc")
    assert validator("not present") == Err("expected one of ['a', 'bc', 'def']")


def test_not_blank() -> None:
    assert NotBlank()("a") == Ok("a")
    assert NotBlank()("") == Err(BLANK_STRING_MSG)
    assert NotBlank()(" ") == Err(BLANK_STRING_MSG)
    assert NotBlank()("\t") == Err(BLANK_STRING_MSG)
    assert NotBlank()("\n") == Err(BLANK_STRING_MSG)


def test_first_of2() -> None:
    str_or_int_validator = OneOf2(String(), Integer())
    assert str_or_int_validator("ok") == Ok(First("ok"))
    assert str_or_int_validator(5) == Ok(Second(5))
    assert str_or_int_validator(5.5) == Err(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )

    str_or_int_validator_named = OneOf2(("name", String()), ("age", Integer()))

    assert str_or_int_validator_named(5.5) == Err(
        {"name": ["expected a string"], "age": ["expected an integer"]}
    )


def test_first_of3() -> None:
    str_or_int_or_float_validator = OneOf3(String(), Integer(), Float())
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
        ("name", String()),
        ("age", Integer()),
        ("alive", Float()),
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

    validator = Obj2Props(prop("name", String()), prop("int", Integer()), into=Person)

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

    def recur_tnel() -> Obj2Props[int, Maybe[TestNonEmptyList], TestNonEmptyList]:
        return nel_validator

    nel_validator: Obj2Props[int, Maybe[TestNonEmptyList], TestNonEmptyList] = Obj2Props(
        prop("val", Integer()),
        maybe_prop("next", Lazy(recur_tnel)),
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
