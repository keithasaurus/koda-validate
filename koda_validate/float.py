from typing import Any

from koda_validate.base import (
    InvalidType,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)


class FloatValidator(_ToTupleValidatorUnsafeScalar[Any, float]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is float:
            return True, val
        else:
            return False, InvalidType(float, "expected a float")
