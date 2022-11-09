from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel, ValidationError, conint, constr
from voluptuous import All, Length, MultipleInvalid, Range, Schema

from koda_validate import (
    IntValidator,
    Max,
    MaxLength,
    Min,
    MinLength,
    RecordValidator,
    StringValidator,
)


@dataclass
class SimpleStr:
    val_1: str
    val_2: int


simple_str_validator = RecordValidator(
    into=SimpleStr,
    keys=(
        ("val_1", StringValidator(MinLength(2), MaxLength(5))),
        ("val_2", IntValidator(Min(1), Max(10))),
    ),
)


def run_kv(objs: List[Any]) -> None:
    for obj in objs:
        if (result := simple_str_validator(obj)).is_valid:
            _ = result.val
        else:
            pass


class ConstrainedModel(BaseModel):
    val_1: constr(strict=True, min_length=2, max_length=5)
    val_2: conint(strict=True, ge=1, le=10)


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        try:
            _ = ConstrainedModel(**obj)
        except ValidationError:
            pass


v_schema = Schema(
    {
        "val_1": All(str, Length(min=2, max=5)),
        "val_2": All(int, Range(min=1, max=10)),
    }
)


def run_v(objs: List[Any]) -> None:
    for obj in objs:
        try:
            v_schema(obj)
        except MultipleInvalid:
            pass


def gen_valid(i: int) -> Dict[str, Any]:
    return {"val_1": f"ok{i}", "val_2": (i % 6) + 2}


def gen_invalid(i: int) -> Dict[str, Any]:
    if i % 2 == 0:
        # too low
        return {"val_1": str(i % 8), "val_2": 0 - i}
    else:
        return {"val_1": f"toolongggg{i}", "val_2": 11 + i}
