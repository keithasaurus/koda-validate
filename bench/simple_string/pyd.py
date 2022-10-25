from pydantic import BaseModel

from bench.utils import catchtime


class BasicString(BaseModel):
    val_1: str


def some_func(val: dict):
    result = BasicString(**val)
    return result


def run() -> float:
    with catchtime() as t:
        for i in range(1_000_000):
            some_func({"val_1": i})
    return t()
