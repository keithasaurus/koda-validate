from typing import Any

from koda_validate import *
from koda_validate import TypeErr, ValidationResult


class SimpleFloatValidator(Validator[float]):
    def __call__(self, val: Any) -> ValidationResult[float]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(TypeErr(float), val, self)


float_validator = SimpleFloatValidator()

test_val = 5.5

assert float_validator(test_val) == Valid(test_val)

assert float_validator(5) == Invalid(TypeErr(float), 5, float_validator)
