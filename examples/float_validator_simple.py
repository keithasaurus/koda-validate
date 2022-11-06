from typing import Any

from koda_validate.base import Serializable, Validator
from koda_validate.validated import Invalid, Valid, Validated


class SimpleFloatValidator(Validator[Any, float, Serializable]):
    def __call__(self, val: Any) -> Validated[float, Serializable]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid("expected a float")


float_validator = SimpleFloatValidator()
float_val = 5.5
assert float_validator(float_val) == Valid(float_val)
assert float_validator(5) == Invalid("expected a float")
