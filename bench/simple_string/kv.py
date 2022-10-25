from koda import Err

from bench.bench_utils import catchtime
from koda_validate import StringValidator
from koda_validate.dictionary import Dict1KeysValidator, key


class SimpleStr:
    def __init__(self, val_1) -> None:
        self.val_1 = val_1


class DumbDict1Keyvalidator(Dict1KeysValidator):
    def __call__(self, data):
        return Err("sad")


def some_func(a):
    return a


string_validator = Dict1KeysValidator(some_func, key("val_1", StringValidator()))


def some_func(val: dict):
    return string_validator(val)


def run() -> float:
    with catchtime() as t:
        for i in range(1_000_000):
            some_func({"val_1": i})
    return t()
