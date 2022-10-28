from dataclasses import dataclass

from pydantic import BaseModel

from koda_validate import DictValidator, IntValidator, StringValidator, key


@dataclass
class SimpleStr:
    val_1: str
    val_2: int


string_validator = DictValidator(
    SimpleStr, key("val_1", StringValidator()), key("val_2", IntValidator())
)


def run_kv(iterations: int) -> None:
    for i in range(iterations):
        string_validator({"val_1": i, "val_2": str(i)})


class BasicString(BaseModel):
    val_1: str
    val_2: int


def run_pyd(iterations: int) -> None:
    for i in range(iterations):
        BasicString(val_1=i, val_2=str(i))
