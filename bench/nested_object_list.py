from dataclasses import dataclass
from typing import Any, List

from koda import Ok
from pydantic import BaseModel

from koda_validate import (
    DictValidator,
    FloatValidator,
    IntValidator,
    ListValidator,
    StringValidator,
    key,
)


@dataclass
class Hobby:
    name: str
    reason: str
    category: str
    enjoyment: float


@dataclass
class Person:
    name: str
    age: int
    hobbies: list[Hobby]


k_validator = DictValidator(
    Person,
    key("name", StringValidator()),
    key("age", IntValidator()),
    key(
        "hobbies",
        ListValidator(
            DictValidator(
                Hobby,
                key("name", StringValidator()),
                key("reason", StringValidator()),
                key("category", StringValidator()),
                key("enjoyment", FloatValidator()),
            )
        ),
    ),
)


class PydHobby(BaseModel):
    name: str
    reason: str
    category: str
    enjoyment: float


# this is not directly equivalent to koda validatel
# because it will implicitly coerce. However it's faster than the
# `con<type>` types, so probably the better to compare against
class PydPerson(BaseModel):
    name: str
    age: str
    hobbies: List[PydHobby]


def get_valid_data(i: int) -> dict[str, Any]:
    return {
        "name": f"name{i}",
        "age": i,
        "hobbies": [
            {
                "name": f"hobby{i}",
                "reason": f"reason{i}",
                "category": f"category{i}",
                "enjoyment": float(i),
            }
            for _ in range(i % 10)
        ],
    }


def run_kv(iterations: int) -> None:
    for i in range(iterations):
        assert isinstance(k_validator(get_valid_data(i)), Ok)


def run_pyd(iterations: int) -> None:
    for i in range(iterations):
        assert isinstance(PydPerson(**get_valid_data(i)), PydPerson)


if __name__ == "__main__":
    print(k_validator(get_valid_data(2)))
    print(PydPerson(**get_valid_data(2)))
