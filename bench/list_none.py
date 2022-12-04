from typing import Any, List

from pydantic import BaseModel, ValidationError

from koda_validate import ListValidator, Valid, none_validator

kv_list_none = ListValidator(none_validator)


def run_kv(objs: List[Any]) -> None:
    for obj in objs:
        if isinstance(result := kv_list_none(obj), Valid):
            _ = result.val
        else:
            _ = result


class BasicString(BaseModel):
    val_1: List[None]


def run_pyd(objs: List[Any]) -> None:
    for obj in objs:
        try:
            _ = BasicString(val_1=obj)
        except ValidationError as e:
            _ = e


def get_obj(i: int) -> Any:
    modded = i % 4
    if modded == 0:
        return [None] * 5
    elif modded == 1:
        return [None, None, None, False] * 2
    elif modded == 2:
        return f"blabla{i}"
    else:
        return [4.423452, "ok", None, False, {"a": 123, "b": "def"}, [1, 2, 3, 4]]
