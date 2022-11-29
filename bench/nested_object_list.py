from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel

from koda_validate import (
    FloatValidator,
    IntValidator,
    ListValidator,
    RecordValidator,
    StringValidator,
)
from koda_validate.dataclasses import DataclassValidator
from koda_validate.validated import Valid


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


k_validator = RecordValidator(
    into=Person,
    keys=(
        ("name", StringValidator()),
        ("age", IntValidator()),
        (
            "hobbies",
            ListValidator(
                RecordValidator(
                    into=Hobby,
                    keys=(
                        ("name", StringValidator()),
                        ("reason", StringValidator()),
                        ("category", StringValidator()),
                        ("enjoyment", FloatValidator()),
                    ),
                )
            ),
        ),
    ),
)

k_dataclass_validator = DataclassValidator(Person)


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
        assert isinstance(k_validator(obj), Valid)


def run_kv_dc(objs: List[Any]) -> None:
    for obj in objs:
        assert isinstance(k_dataclass_validator(obj), Valid)


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        assert isinstance(PydPerson(**obj), PydPerson)


if __name__ == "__main__":
    print(k_validator(get_valid_data(2)))
    print(PydPerson(**get_valid_data(2)))
