from typing import Any

from koda import Err, Ok, Result

from koda_validate.typedefs import JSONValue, Validator


class SimpleFloatValidator(Validator[Any, float, JSONValue]):
    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return Ok(val)
        else:
            return Err("expected a float")


float_validator = SimpleFloatValidator()
float_val = 5.5
assert float_validator(float_val) == Ok(float_val)
assert float_validator(5) == Err("expected a float")
