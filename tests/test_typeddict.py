from typing import TypedDict

from koda_validate.base import Valid
from koda_validate.typeddict import TypedDictValidator


class PersonSimpleTD(TypedDict):
    name: str
    age: int


def test_valid_dict_returns_dataclass_result() -> None:
    assert TypedDictValidator(PersonSimpleTD)({"name": "bob", "age": 100}) == Valid(
        {"name": "bob", "age": 100}
    )
