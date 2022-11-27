from typing import Any

from koda_validate.base import (
    InvalidType,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)


class BoolValidator(_ToTupleValidatorUnsafeScalar[Any, bool]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is bool:
            return True, val
        else:
            return False, InvalidType(bool, "expected a boolean", self)
