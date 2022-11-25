from typing import Any, Final, Literal, Tuple

from koda_validate.base import (
    InvalidType,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_FLOAT_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, (
    InvalidType(float, "expected a float")
)


class FloatValidator(_ToTupleValidatorUnsafeScalar[Any, float]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is float:
            return True, val
        else:
            return EXPECTED_FLOAT_ERR
