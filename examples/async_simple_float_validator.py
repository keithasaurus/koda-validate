import asyncio
from typing import Any

from koda_validate import *
from koda_validate.base import TypeErr, ValidationResult


class SimpleFloatValidator(Validator[float]):

    # this validator doesn't do any IO, so we can just use the `__call__` method
    async def validate_async(self, val: Any) -> ValidationResult[float]:
        return self(val)

    def __call__(self, val: Any) -> ValidationResult[float]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(TypeErr(float), val, self)


float_validator = SimpleFloatValidator()

test_val = 5.5

assert asyncio.run(float_validator.validate_async(test_val)) == Valid(test_val)

assert asyncio.run(float_validator.validate_async(5)) == Invalid(
    TypeErr(float), 5, float_validator
)
