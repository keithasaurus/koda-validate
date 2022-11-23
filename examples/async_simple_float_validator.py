import asyncio
from typing import Any

from koda_validate import *
from koda_validate.base import TypeErr, ValidationErr


class SimpleFloatValidator(Validator[Any, float]):
    def __call__(self, val: Any) -> Validated[float, ValidationErr]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(TypeErr(float, "expected a float"))

    # this validator doesn't do any IO, so we can just use the `__call__` method
    async def validate_async(self, val: Any) -> Validated[float, ValidationErr]:
        return self(val)


float_validator = SimpleFloatValidator()

test_val = 5.5

assert asyncio.run(float_validator.validate_async(test_val)) == Valid(test_val)

assert asyncio.run(float_validator.validate_async(5)) == Invalid(
    TypeErr(float, "expected a float")
)
