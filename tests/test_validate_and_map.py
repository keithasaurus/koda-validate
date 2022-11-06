from dataclasses import dataclass

from koda_validate._validate_and_map import validate_and_map
from koda_validate.typedefs import Invalid, Valid


def test_map_1() -> None:
    def string_thing(s: str) -> str:
        return f"valid {s}"

    assert validate_and_map(
        string_thing,
        Invalid("just returns failure"),
    ) == Invalid(("just returns failure",))

    assert validate_and_map(string_thing, Valid("hooray")) == Valid("valid hooray")


def test_map_2() -> None:
    @dataclass
    class Person2:
        name: str
        age: int

    assert validate_and_map(
        Person2, Invalid("invalid name"), Invalid("invalid age")
    ) == Invalid(("invalid name", "invalid age"))

    assert validate_and_map(Person2, Valid("Bob"), Invalid("invalid age")) == Invalid(
        ("invalid age",)
    )

    assert validate_and_map(Person2, Valid("Bob"), Valid(25)) == Valid(
        Person2(name="Bob", age=25)
    )


def test_map_3() -> None:
    @dataclass
    class Person:
        first_name: str
        last_name: str
        age: int

    assert validate_and_map(
        Person,
        Invalid("invalid first name"),
        Invalid("invalid last name"),
        Invalid("invalid age"),
    ) == Invalid(("invalid first name", "invalid last name", "invalid age"))

    assert validate_and_map(
        Person, Invalid("invalid first name"), Invalid("invalid last name"), Valid(25)
    ) == Invalid(("invalid first name", "invalid last name"))

    assert validate_and_map(
        Person, Invalid("invalid first name"), Valid("Smith"), Valid(25)
    ) == Invalid(("invalid first name",))

    assert validate_and_map(Person, Valid("John"), Valid("Doe"), Valid(25)) == Valid(
        Person(first_name="John", last_name="Doe", age=25)
    )
