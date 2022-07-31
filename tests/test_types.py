from dataclasses import dataclass
from enum import Enum

from koda import Err, Ok

from koda_validate.validators.validate_and_map import validate_and_map


def test_map_1() -> None:
    def string_thing(s: str) -> str:
        return f"valid {s}"

    assert validate_and_map(
        string_thing,
        Err("just returns failure"),
    ) == Err(("just returns failure",))

    assert validate_and_map(string_thing, Ok("hooray")) == Ok("valid hooray")


def test_map_2() -> None:
    @dataclass
    class Person2:
        name: str
        age: int

    assert validate_and_map(Person2, Err("invalid name"), Err("invalid age")) == Err(
        ("invalid name", "invalid age")
    )

    assert validate_and_map(Person2, Ok("Bob"), Err("invalid age")) == Err(
        ("invalid age",)
    )

    assert validate_and_map(Person2, Ok("Bob"), Ok(25)) == Ok(Person2(name="Bob", age=25))


def test_map_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    assert validate_and_map(
        Person, Err("invalid first name"), Err("invalid last name"), Err("invalid age")
    ) == Err(("invalid first name", "invalid last name", "invalid age"))

    assert validate_and_map(
        Person, Err("invalid first name"), Err("invalid last name"), Ok(25)
    ) == Err(("invalid first name", "invalid last name"))

    assert validate_and_map(
        Person, Err("invalid first name"), Ok("Smith"), Ok(25)
    ) == Err(("invalid first name",))

    assert validate_and_map(Person, Ok("John"), Ok("Doe"), Ok(25)) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
    ) == Err(
        ("invalid first name", "invalid last name", "invalid age", "invalid eye color")
    )

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person, Err("invalid first name"), Ok("Smith"), Ok(25), Err("invalid eye color")
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(Person, Ok("John"), Ok("Doe"), Ok(25), Ok("brown")) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
        Err("invalid -- people can't fly"),
    ) == Err(
        (
            "invalid first name",
            "invalid last name",
            "invalid age",
            "invalid eye color",
            "invalid -- people can't fly",
        )
    )

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Ok("Smith"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        Person, Ok("John"), Ok("Doe"), Ok(25), Ok("brown"), Ok(False)
    ) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
        Err("invalid -- people can't fly"),
        Err("invalid -- beginners not allowed"),
    ) == Err(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Ok("Smith"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Ok("John"),
        Ok("Doe"),
        Ok(25),
        Ok("brown"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
    ) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
        Err("invalid -- people can't fly"),
        Err("invalid -- beginners not allowed"),
        Err("invalid number of fingers"),
    ) == Err(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Ok("Smith"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Ok("John"),
        Ok("Doe"),
        Ok(25),
        Ok("brown"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
    ) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
        Err("invalid -- people can't fly"),
        Err("invalid -- beginners not allowed"),
        Err("invalid number of fingers"),
        Err("invalid number of toes"),
    ) == Err(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Ok("Smith"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Ok("John"),
        Ok("Doe"),
        Ok(25),
        Ok("brown"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
    ) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
        Err("invalid -- people can't fly"),
        Err("invalid -- beginners not allowed"),
        Err("invalid number of fingers"),
        Err("invalid number of toes"),
        Err("invalid country"),
    ) == Err(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
        Ok("USA"),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Ok("smith"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
        Ok("USA"),
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Ok("John"),
        Ok("Doe"),
        Ok(25),
        Ok("brown"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
        Ok("USA"),
    ) == Ok(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Err("invalid age"),
        Err("invalid eye color"),
        Err("invalid -- people can't fly"),
        Err("invalid -- beginners not allowed"),
        Err("invalid number of fingers"),
        Err("invalid number of toes"),
        Err("invalid country"),
        Err("invalid region"),
    ) == Err(
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
        Person,
        Err("invalid first name"),
        Err("invalid last name"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
        Ok("USA"),
        Ok("California"),
    ) == Err(("invalid first name", "invalid last name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Err("invalid first name"),
        Ok("smith"),
        Ok(25),
        Err("invalid eye color"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
        Ok("USA"),
        Ok("California"),
    ) == Err(("invalid first name", "invalid eye color"))

    assert validate_and_map(
        Person,
        Ok("John"),
        Ok("Doe"),
        Ok(25),
        Ok("brown"),
        Ok(False),
        Ok(SwimmingLevel.ADVANCED),
        Ok(9.5),
        Ok(3.1),
        Ok("USA"),
        Ok("California"),
    ) == Ok(
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
