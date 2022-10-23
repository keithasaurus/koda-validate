import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from decimal import Decimal as DecimalStdLib
from typing import Any, Dict, List, Protocol, Tuple

from koda.either import First, Second, Third
from koda.maybe import Just, Maybe, nothing
from koda.result import Err, Ok, Result

from koda_validate.boolean import BooleanValidator
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import (
    Dict2KeysValidator,
    Dict4KeysValidator,
    Dict5KeysValidator,
    Dict6KeysValidator,
    Dict7KeysValidator,
    Dict8KeysValidator,
    Dict9KeysValidator,
    Dict10KeysValidator,
    MapValidator,
    MaxKeys,
    MinKeys,
    dict_validator,
    key,
    maybe_key,
)
from koda_validate.float import FloatValidator
from koda_validate.generic import Choices, Exactly, Lazy, Max, Min, MultipleOf
from koda_validate.integer import IntValidator
from koda_validate.list import ListValidator, MaxItems, MinItems, unique_items
from koda_validate.none import OptionalValidator, none_validator
from koda_validate.one_of import OneOf2, OneOf3
from koda_validate.string import (
    BLANK_STRING_MSG,
    Email,
    MaxLength,
    NotBlank,
    RegexPredicate,
    StringValidator,
)
from koda_validate.time import DatetimeValidator, DateValidator
from koda_validate.tuple import Tuple2Validator, Tuple3Validator
from koda_validate.typedefs import JSONValue, Predicate
from koda_validate.utils import OBJECT_ERRORS_FIELD


def test_decimal() -> None:
    assert DecimalValidator()("a string") == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert DecimalValidator()(5.5) == Err(
        ["expected a decimal-compatible string or integer"]
    )

    assert DecimalValidator()(DecimalStdLib("5.5")) == Ok(DecimalStdLib("5.5"))

    assert DecimalValidator()(5) == Ok(DecimalStdLib(5))

    assert DecimalValidator(Min(DecimalStdLib(4)), Max(DecimalStdLib("5.5")))(5) == Ok(
        DecimalStdLib(5)
    )


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


def test_date_validator() -> None:
    assert DateValidator()("2021-03-21") == Ok(date(2021, 3, 21))
    assert DateValidator()("2021-3-21") == Err(["expected date formatted as yyyy-mm-dd"])


def test_datetime_validator() -> None:
    assert DatetimeValidator()("") == Err(["expected iso8601-formatted string"])
    assert DatetimeValidator()("2011-11-04") == Ok(datetime(2011, 11, 4, 0, 0))
    assert DatetimeValidator()("2011-11-04T00:05:23") == Ok(
        datetime(2011, 11, 4, 0, 5, 23)
    )


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

    assert IntValidator(Min(2), Max(10), DivisibleBy2(),)(
        11
    ) == Err(["maximum allowed value is 10", "must be divisible by 2"])


def test_optional_validator() -> None:
    assert OptionalValidator(StringValidator())(None) == Ok(None)
    assert OptionalValidator(StringValidator())(5) == Err(
        val={"variant 1": ["must be None"], "variant 2": ["expected a string"]}
    )
    assert OptionalValidator(StringValidator())("okok") == Ok("okok")


def test_map_validator() -> None:
    assert MapValidator(StringValidator(), StringValidator())(5) == Err(
        {"__container__": ["expected a map"]}
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


def test_max_items() -> None:
    assert MaxItems(0)([]) == Ok([])

    assert MaxItems(5)([1, 2, 3]) == Ok([1, 2, 3])

    assert MaxItems(5)(["a", "b", "c", "d", "e", "fghij"]) == Err(
        "maximum allowed length is 5"
    )


def test_min_items() -> None:
    assert MinItems(0)([]) == Ok([])

    assert MinItems(3)([1, 2, 3]) == Ok([1, 2, 3])

    assert MinItems(3)([1, 2]) == Err("minimum allowed length is 3")


def test_max_properties() -> None:
    assert MaxKeys(0)({}) == Ok({})

    assert MaxKeys(5)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MaxKeys(1)({"a": 1, "b": 2}) == Err("maximum allowed properties is 1")


def test_min_properties() -> None:
    assert MinKeys(0)({}) == Ok({})

    assert MinKeys(3)({"a": 1, "b": 2, "c": 3}) == Ok({"a": 1, "b": 2, "c": 3})

    assert MinKeys(3)({"a": 1, "b": 2}) == Err("minimum allowed properties is 3")


def test_tuple2() -> None:
    assert Tuple2Validator(StringValidator(), IntValidator())({}) == Err(
        {"__container__": ["expected list or tuple of length 2"]}
    )

    assert Tuple2Validator(StringValidator(), IntValidator())([]) == Err(
        {"__container__": ["expected list or tuple of length 2"]}
    )

    assert Tuple2Validator(StringValidator(), IntValidator())(["a", 1]) == Ok(("a", 1))
    assert Tuple2Validator(StringValidator(), IntValidator())(("a", 1)) == Ok(("a", 1))

    assert Tuple2Validator(StringValidator(), IntValidator())([1, "a"]) == Err(
        {"0": ["expected a string"], "1": ["expected an integer"]}
    )

    def must_be_a_if_integer_is_1(
        ab: Tuple[str, int]
    ) -> Result[Tuple[str, int], JSONValue]:
        if ab[1] == 1:
            if ab[0] == "a":
                return Ok(ab)
            else:
                return Err({"__container__": ["must be a if int is 1"]})
        else:
            return Ok(ab)

    a1_validator = Tuple2Validator(
        StringValidator(), IntValidator(), must_be_a_if_integer_is_1
    )

    assert a1_validator(["a", 1]) == Ok(("a", 1))
    assert a1_validator(["b", 1]) == Err({"__container__": ["must be a if int is 1"]})
    assert a1_validator(["b", 2]) == Ok(("b", 2))


def test_tuple3() -> None:
    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        {}
    ) == Err({"__container__": ["expected list or tuple of length 3"]})

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        []
    ) == Err({"__container__": ["expected list or tuple of length 3"]})

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        ["a", 1, False]
    ) == Ok(("a", 1, False))

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        ("a", 1, False)
    ) == Ok(("a", 1, False))

    assert Tuple3Validator(StringValidator(), IntValidator(), BooleanValidator())(
        [1, "a", 7.42]
    ) == Err(
        {
            "0": ["expected a string"],
            "1": ["expected an integer"],
            "2": ["expected a boolean"],
        }
    )

    def must_be_a_if_1_and_true(
        abc: Tuple[str, int, bool]
    ) -> Result[Tuple[str, int, bool], JSONValue]:
        if abc[1] == 1 and abc[2] is True:
            if abc[0] == "a":
                return Ok(abc)
            else:
                return Err({"__container__": ["must be a if int is 1 and bool is True"]})
        else:
            return Ok(abc)

    a1_validator = Tuple3Validator(
        StringValidator(), IntValidator(), BooleanValidator(), must_be_a_if_1_and_true
    )

    assert a1_validator(["a", 1, True]) == Ok(("a", 1, True))
    assert a1_validator(["b", 1, True]) == Err(
        {"__container__": ["must be a if int is 1 and bool is True"]}
    )
    assert a1_validator(["b", 2, False]) == Ok(("b", 2, False))


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


class PersonLike(Protocol):
    last_name: str
    eye_color: str


_JONES_ERROR_MSG: JSONValue = {
    "__container__": ["can't have last_name of jones and eye color of brown"]
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


def test_one_of2() -> None:
    str_or_int_validator = OneOf2(StringValidator(), IntValidator())
    assert str_or_int_validator("ok") == Ok(First("ok"))
    assert str_or_int_validator(5) == Ok(Second(5))
    assert str_or_int_validator(5.5) == Err(
        {"variant 1": ["expected a string"], "variant 2": ["expected an integer"]}
    )


def test_one_of3() -> None:
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


def test_email() -> None:
    assert Email()("notanemail") == Err("expected a valid email address")
    assert Email()("a@b.com") == Ok("a@b.com")

    custom_regex_validator = Email(re.compile(r"[a-z.]+@somecompany\.com"))
    assert custom_regex_validator("a.b@somecompany.com") == Ok("a.b@somecompany.com")
    assert custom_regex_validator("a.b@example.com") == Err(
        "expected a valid email address"
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
        TestNonEmptyList,
        key("val", IntValidator()),
        maybe_key("next", Lazy(recur_tnel)),
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
    assert RegexPredicate(re.compile(r".+"))("something") == Ok("something")
    assert RegexPredicate(re.compile(r".+"))("") == Err("must match pattern .+")


def test_multiple_of() -> None:
    assert MultipleOf(5)(10) == Ok(10)
    assert MultipleOf(5)(11) == Err("expected multiple of 5")
    assert MultipleOf(2.2)(4.40) == Ok(4.40)


def test_exactly() -> None:
    assert Exactly(5)(5) == Ok(5)
    assert Exactly(5)(4) == Err("expected 5")
    assert Exactly("ok")("ok") == Ok("ok")
    assert Exactly("ok")("not ok") == Err('expected "ok"')
    assert Exactly(Decimal("1.25"))(Decimal("1.25")) == Ok(Decimal("1.25"))
    assert Exactly(Decimal("1.1"))(Decimal("5")) == Err("expected 1.1")
