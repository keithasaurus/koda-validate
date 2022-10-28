from dataclasses import dataclass
from typing import Any, Dict, List

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
    hobbies: List[Hobby]


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


def get_valid_data(i: int) -> Dict[str, Any]:
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


def run_kv(objs: List[Any]) -> None:
    for obj in objs:
        assert isinstance(k_validator(obj), Ok)


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        assert isinstance(PydPerson(**obj), PydPerson)


if __name__ == "__main__":
    print(k_validator(get_valid_data(2)))
    print(PydPerson(**get_valid_data(2)))
