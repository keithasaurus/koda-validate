from dataclasses import dataclass

from koda import Err, Ok

from koda_validate._validate_and_map import validate_and_map


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
