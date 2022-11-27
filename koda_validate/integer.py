from typing import Any

from koda_validate.base import (
    InvalidType,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)


class IntValidator(_ToTupleValidatorUnsafeScalar[Any, int]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is int:
            return True, val
        else:
            return False, (InvalidType(int, "expected an integer", self))
