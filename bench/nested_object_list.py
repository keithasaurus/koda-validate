from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple, TypedDict

from pydantic import BaseModel

from koda_validate import (
    DictValidatorAny,
    FloatValidator,
    IntValidator,
    ListValidator,
    RecordValidator,
    StringValidator,
)
from koda_validate.dataclasses import DataclassValidator
from koda_validate.namedtuple import NamedTupleValidator
from koda_validate.typeddict import TypedDictValidator


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


class HobbyNT(NamedTuple):
    name: str
    reason: str
    category: str
    enjoyment: float


class PersonNT(NamedTuple):
    name: str
    age: int
    hobbies: List[HobbyNT]


class HobbyTD(TypedDict):
    name: str
    reason: str
    category: str
    enjoyment: float


class PersonTD(TypedDict):
    name: str
    age: int
    hobbies: List[HobbyTD]


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
k_namedtuple_validator = NamedTupleValidator(PersonNT)
k_typeddict_validator = TypedDictValidator(PersonTD)

k_dict_any_validator = DictValidatorAny(
    {
        "name": StringValidator(),
        "age": IntValidator(),
        "hobbies": ListValidator(
            DictValidatorAny(
                {
                    "name": StringValidator(),
                    "reason": StringValidator(),
                    "category": StringValidator(),
                    "enjoyment": FloatValidator(),
                }
            ),
        ),
    }
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


def get_data(i: int) -> Dict[str, Any]:
    modded = i % 3
    if modded == 0:
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
    elif modded == 1:
        return {
            "name": None,
            "age": i,
            "hobbies": [
                {
                    "name": f"hobby{i}",
                    "reason": f"reason{i}",
                    "enjoyment": float(i),
                }
                for _ in range(i % 10)
            ],
        }
    else:
        return {
            "name": f"name{i}",
            "age": i,
            "hobbies": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        }


def run_kv(objs: List[Any]) -> None:
    for obj in objs:
        _ = k_validator(obj)


def run_kv_dc(objs: List[Any]) -> None:
    for obj in objs:
        _ = k_dataclass_validator(obj)


def run_kv_dict_any(objs: List[Any]) -> None:
    for obj in objs:
        _ = k_dict_any_validator(obj)


def run_kv_nt(objs: List[Any]) -> None:
    for obj in objs:
        _ = k_namedtuple_validator(obj)


def run_kv_td(objs: List[Any]) -> None:
    for obj in objs:
        _ = k_typeddict_validator(obj)


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        try:
            _ = PydPerson(**obj)
        except:  # noqa: E722
            pass


if __name__ == "__main__":
    print(k_validator(get_data(2)))
    print(PydPerson(**get_data(2)))
