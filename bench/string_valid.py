from typing import Any, List

from pydantic import BaseModel, ValidationError, constr

from koda_validate import StringValidator, Valid

string_validator = StringValidator()


def run_kv(objs: List[Any]) -> None:
    for obj in objs:
        if isinstance(result := string_validator(obj), Valid):
            _ = result.val
        else:
            _ = result.val


class BasicString(BaseModel):
    val_1: constr(strict=True)


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        try:
            _ = BasicString(val_1=obj)
        except ValidationError as e:
            _ = e


def get_str(i: int) -> str:
    return f"the_str_{i}"
