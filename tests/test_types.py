from dataclasses import dataclass
from enum import Enum

from koda import err, ok

from koda_validate.utils import validate_and_map


def test_map_1() -> None:
    def string_thing(s: str) -> str:
        return f"valid {s}"

    assert validate_and_map(
        err("just returns failure"),
        string_thing,
    ) == err(("just returns failure",))

    assert validate_and_map(ok("hooray"), string_thing) == ok("valid hooray")


def test_map_2() -> None:
    @dataclass
    class Person2:
        name: str
        age: int

    assert validate_and_map(err("invalid name"), err("invalid age"), Person2) == err(
        ("invalid name", "invalid age")
    )

    assert validate_and_map(ok("Bob"), err("invalid age"), Person2) == err(
        ("invalid age",)
    )

    assert validate_and_map(ok("Bob"), ok(25), Person2) == ok(Person2(name="Bob", age=25))


def test_map_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    assert validate_and_map(
        err("invalid first name"), err("invalid last name"), err("invalid age"), Person
    ) == err(("invalid first name", "invalid last name", "invalid age"))

    assert validate_and_map(
        err("invalid first name"), err("invalid last name"), ok(25), Person
    ) == err(("invalid first name", "invalid last name"))

    assert validate_and_map(
        err("invalid first name"), ok("Smith"), ok(25), Person
    ) == err(("invalid first name",))

    assert validate_and_map(ok("John"), ok("Doe"), ok(25), Person) == ok(
        Person(first_name="John", last_name="Doe", age=25)
    )


def test_map_4() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        Person,
    ) == err(
        ("invalid first name", "invalid last name", "invalid age", "invalid eye color")
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"), ok("Smith"), ok(25), err("invalid eye color"), Person
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(ok("John"), ok("Doe"), ok(25), ok("brown"), Person) == ok(
        Person(first_name="John", last_name="Doe", age=25, eye_color="brown")
    )


def test_map_5() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        err("invalid -- people can't fly"),
        Person,
    ) == err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
        )
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"),
        ok("Smith"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        Person,
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        ok("John"), ok("Doe"), ok(25), ok("brown"), ok(False), Person
    ) == ok(
        Person(
            first_name="John", last_name="Doe", age=25, eye_color="brown", can_fly=False
        )
    )


def test_map_6() -> None:
    class SwimmingLevel(Enum):
        BEGINNER = 1
        INTERMEDIATE = 2
        ADVANCED = 3

    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        swimming_level: SwimmingLevel

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        err("invalid -- people can't fly"),
        err("invalid -- beginners not allowed"),
        Person,
    ) == err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
            "invalid -- beginners not allowed",
        )
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"),
        ok("Smith"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        Person,
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        ok("John"),
        ok("Doe"),
        ok(25),
        ok("brown"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        Person,
    ) == ok(
        Person(
            first_name="John",
            last_name="Doe",
            age=25,
            eye_color="brown",
            can_fly=False,
            swimming_level=SwimmingLevel.ADVANCED,
        )
    )


def test_map_7() -> None:
    class SwimmingLevel(Enum):
        BEGINNER = 1
        INTERMEDIATE = 2
        ADVANCED = 3

    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        swimming_level: SwimmingLevel
        number_of_fingers: float

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        err("invalid -- people can't fly"),
        err("invalid -- beginners not allowed"),
        err("invalid number of fingers"),
        Person,
    ) == err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
            "invalid -- beginners not allowed",
            "invalid number of fingers",
        )
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"),
        ok("Smith"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        Person,
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        ok("John"),
        ok("Doe"),
        ok(25),
        ok("brown"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        Person,
    ) == ok(
        Person(
            first_name="John",
            last_name="Doe",
            age=25,
            eye_color="brown",
            can_fly=False,
            swimming_level=SwimmingLevel.ADVANCED,
            number_of_fingers=9.5,
        )
    )


def test_map_8() -> None:
    class SwimmingLevel(Enum):
        BEGINNER = 1
        INTERMEDIATE = 2
        ADVANCED = 3

    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        swimming_level: SwimmingLevel
        number_of_fingers: float
        number_of_toes: float

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        err("invalid -- people can't fly"),
        err("invalid -- beginners not allowed"),
        err("invalid number of fingers"),
        err("invalid number of toes"),
        Person,
    ) == err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
            "invalid -- beginners not allowed",
            "invalid number of fingers",
            "invalid number of toes",
        )
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"),
        ok("Smith"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        Person,
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        ok("John"),
        ok("Doe"),
        ok(25),
        ok("brown"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        Person,
    ) == ok(
        Person(
            first_name="John",
            last_name="Doe",
            age=25,
            eye_color="brown",
            can_fly=False,
            swimming_level=SwimmingLevel.ADVANCED,
            number_of_fingers=9.5,
            number_of_toes=3.1,
        )
    )


def test_map_9() -> None:
    class SwimmingLevel(Enum):
        BEGINNER = 1
        INTERMEDIATE = 2
        ADVANCED = 3

    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        swimming_level: SwimmingLevel
        number_of_fingers: float
        number_of_toes: float
        country: str

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        err("invalid -- people can't fly"),
        err("invalid -- beginners not allowed"),
        err("invalid number of fingers"),
        err("invalid number of toes"),
        err("invalid country"),
        Person,
    ) == err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
            "invalid -- beginners not allowed",
            "invalid number of fingers",
            "invalid number of toes",
            "invalid country",
        )
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        ok("USA"),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"),
        ok("smith"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        ok("USA"),
        Person,
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        ok("John"),
        ok("Doe"),
        ok(25),
        ok("brown"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        ok("USA"),
        Person,
    ) == ok(
        Person(
            first_name="John",
            last_name="Doe",
            age=25,
            eye_color="brown",
            can_fly=False,
            swimming_level=SwimmingLevel.ADVANCED,
            number_of_fingers=9.5,
            number_of_toes=3.1,
            country="USA",
        )
    )


def test_map_10() -> None:
    class SwimmingLevel(Enum):
        BEGINNER = 1
        INTERMEDIATE = 2
        ADVANCED = 3

    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int
        eye_color: str
        can_fly: bool
        swimming_level: SwimmingLevel
        number_of_fingers: float
        number_of_toes: float
        country: str
        region: str

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        err("invalid age"),
        err("invalid eye color"),
        err("invalid -- people can't fly"),
        err("invalid -- beginners not allowed"),
        err("invalid number of fingers"),
        err("invalid number of toes"),
        err("invalid country"),
        err("invalid region"),
        Person,
    ) == err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
            "invalid -- beginners not allowed",
            "invalid number of fingers",
            "invalid number of toes",
            "invalid country",
            "invalid region",
        )
    )

    assert validate_and_map(
        err("invalid first name"),
        err("invalid last name"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        ok("USA"),
        ok("California"),
        Person,
    ) == err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        err("invalid first name"),
        ok("smith"),
        ok(25),
        err("invalid eye color"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        ok("USA"),
        ok("California"),
        Person,
    ) == err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        ok("John"),
        ok("Doe"),
        ok(25),
        ok("brown"),
        ok(False),
        ok(SwimmingLevel.ADVANCED),
        ok(9.5),
        ok(3.1),
        ok("USA"),
        ok("California"),
        Person,
    ) == ok(
        Person(
            first_name="John",
            last_name="Doe",
            age=25,
            eye_color="brown",
            can_fly=False,
            swimming_level=SwimmingLevel.ADVANCED,
            number_of_fingers=9.5,
            number_of_toes=3.1,
            country="USA",
            region="California",
        )
    )
