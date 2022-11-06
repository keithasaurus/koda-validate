from typing import Any

from koda_validate.typedefs import Err, Ok, Result, Serializable, Validator


class SimpleFloatValidator(Validator[Any, float, Serializable]):
    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return Ok(val)
        else:
            return Err("expected a float")


float_validator = SimpleFloatValidator()
float_val = 5.5
assert float_validator(float_val) == Ok(float_val)
assert float_validator(5) == Err("expected a float")
