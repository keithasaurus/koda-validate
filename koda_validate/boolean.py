from typing import Any, Final, Literal, Tuple

from koda_validate.base import (
    InvalidType,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_BOOL_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, InvalidType(
    bool, "expected a boolean"
)


class BoolValidator(_ToTupleValidatorUnsafeScalar[Any, bool]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is bool:
            return True, val
        else:
            return EXPECTED_BOOL_ERR
