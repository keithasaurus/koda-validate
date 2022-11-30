from typing import Any

from koda_validate import *
from koda_validate.base import InvalidType, Validated


class SimpleFloatValidator(Validator[float]):
    def __call__(self, val: Any) -> Validated[float]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(InvalidType(self, float))


float_validator = SimpleFloatValidator()

test_val = 5.5

assert float_validator(test_val) == Valid(test_val)

assert float_validator(5) == Invalid(InvalidType(float_validator, float))
