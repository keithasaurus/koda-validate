from dataclasses import dataclass

from pydantic import BaseModel

from koda_validate import StringValidator
from koda_validate.dictionary import dict_validator, key


@dataclass
class SimpleStr:
    val_1: str


string_validator = dict_validator(SimpleStr, key("val_1", StringValidator()))


def run_kv(iterations: int) -> None:
    for i in range(iterations):
        string_validator({"val_1": i})


class BasicString(BaseModel):
    val_1: str


def run_pyd(iterations: int) -> None:
    for i in range(iterations):
        BasicString(val_1=i)
