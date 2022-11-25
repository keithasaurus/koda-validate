from typing import Any, Final, Literal, Tuple

from koda_validate.base import (
    InvalidType,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_INTEGER_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, (
    InvalidType(int, "expected an integer")
)


class IntValidator(_ToTupleValidatorUnsafeScalar[Any, int]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is int:
            return True, val
        else:
            return EXPECTED_INTEGER_ERR
