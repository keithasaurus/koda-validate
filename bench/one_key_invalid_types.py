from dataclasses import dataclass

from koda import Ok
from pydantic import BaseModel, ValidationError, constr

from koda_validate import DictValidator, StringValidator, key


@dataclass
class SimpleStr:
    val_1: str


string_validator = DictValidator(SimpleStr, key("val_1", StringValidator()))


def run_kv(iterations: int) -> None:
    for i in range(iterations):
        if isinstance(result := string_validator({"val_1": i}), Ok):
            _ = result.val
        else:
            _ = result.val


class BasicString(BaseModel):
    val_1: constr(strict=True)


def run_pyd(iterations: int) -> None:
    for i in range(iterations):
        try:
            _ = BasicString(val_1=i)
        except ValidationError as e:
            _ = e
