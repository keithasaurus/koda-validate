from dataclasses import dataclass
from typing import Any, List

from pydantic import BaseModel
from voluptuous import Schema

from koda_validate import IntValidator, RecordValidator, StringValidator


@dataclass
class SimpleStr:
    val_1: str
    val_2: int


string_validator = RecordValidator(
    into=SimpleStr, keys=(("val_1", StringValidator()), ("val_2", IntValidator()))
)


def run_kv(objs: List[Any]) -> None:
    for obj in objs:
        string_validator(obj)


class BasicString(BaseModel):
    val_1: str
    val_2: int


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        BasicString(**obj)


v_schema = Schema(
    {
        "val_1": str,
        "val_2": int,
    }
)


def run_v(objs: List[Any]) -> None:
    for obj in objs:
        v_schema(obj)
