from dataclasses import dataclass

from koda import Err, Ok
from pydantic import BaseModel, ValidationError, constr

from koda_validate import StringValidator, key
from koda_validate.dictionary import dict_validator


@dataclass
class SimpleStr:
    val_1: str


string_validator = dict_validator(SimpleStr, key("val_1", StringValidator()))


def run_kv(iterations: int) -> None:
    for i in range(iterations):
        match string_validator({"val_1": i}):
            case Ok(val):
                _ = val
            case Err(val):
                _ = val


class BasicString(BaseModel):
    val_1: constr(strict=True)


def run_pyd(iterations: int) -> None:
    for i in range(iterations):
        try:
            BasicString(val_1=i)
        except ValidationError as e:
            _ = e
