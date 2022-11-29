from typing import Any

from koda_validate import *
from koda_validate.base import InvalidType, ValidationResult


class SimpleFloatValidator(Validator[Any, float]):
    def __call__(self, val: Any) -> ValidationResult[float]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(InvalidType(self, float))


float_validator = SimpleFloatValidator()

test_val = 5.5

assert float_validator(test_val) == Valid(test_val)

assert float_validator(5) == Invalid(InvalidType(float_validator, float))
