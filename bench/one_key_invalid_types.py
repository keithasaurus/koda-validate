from dataclasses import dataclass
from typing import Any, List

from koda import Ok
from pydantic import BaseModel, ValidationError, constr

from koda_validate import DictValidator, StringValidator, key


@dataclass
class SimpleStr:
    val_1: str


string_validator = DictValidator(SimpleStr, key("val_1", StringValidator()))


def run_kv(objs: Any) -> None:
    for obj in objs:
        if isinstance(result := string_validator(obj), Ok):
            _ = result.val
        else:
            _ = result.val


class BasicString(BaseModel):
    val_1: constr(strict=True)


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        try:
            _ = BasicString(**obj)
        except ValidationError as e:
            _ = e
