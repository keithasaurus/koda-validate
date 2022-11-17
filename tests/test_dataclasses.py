from dataclasses import dataclass

from koda_validate import Invalid, Valid
from koda_validate.dataclasses import DataclassValidator


@dataclass
class PersonSimple:
    name: str
    age: int


def test_will_fail_if_not_dataclass() -> None:
    assert DataclassValidator(PersonSimple)(None) == Invalid(
        ["expected a dict or PersonSimple instance"]
    )


def test_wrong_dataclass_is_invalid() -> None:
    @dataclass
    class Other:
        name: str
        age: int

    assert DataclassValidator(PersonSimple)(Other("ok", 5)) == Invalid(
        ["expected a dict or PersonSimple instance"]
    )


def test_valid_dict_returns_dataclass_result() -> None:
    assert DataclassValidator(PersonSimple)({"name": "bob", "age": 100}) == Valid(
        PersonSimple("bob", 100)
    )


def test_valid_dataclass_returns_dataclass_result() -> None:
    result = DataclassValidator(PersonSimple)(PersonSimple("alice", 99))

    assert result == Valid(PersonSimple("alice", 99))


def test_validates_proper_string_type() -> None:
    @dataclass
    class Example:
        name: str

    dc_validator = DataclassValidator(Example)

    assert dc_validator(Example("ok")) == Valid(Example("ok"))
    assert dc_validator(Example(5)) == Invalid({"name": ["expected a string"]})


# def test_will_fail_if_not_exact_dataclass() -> None:
