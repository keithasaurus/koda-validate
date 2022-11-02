from dataclasses import dataclass
from typing import Any, List

from pydantic import BaseModel

from koda_validate import DictValidator, IntValidator, StringValidator


@dataclass
class SimpleStr:
    val_1: str
    val_2: int


string_validator = DictValidator(
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
