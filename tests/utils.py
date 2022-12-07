from typing import Any

from koda_validate import Invalid, Valid, Validator
from koda_validate.base import TypeErr, ValidationResult


class BasicNoneValidator(Validator[None]):
    """
    Since most validators are _ToTuplevalidatorUnsafe*, this gives us a
    way to make sure we are still exercising the normal `Validator` paths
    """

    async def validate_async(self, val: Any) -> ValidationResult[None]:
        return self(val)

    def __call__(self, val: Any) -> ValidationResult[None]:
        if val is None:
            return Valid(None)
        else:
            return Invalid(TypeErr(type(None)), val, self)
