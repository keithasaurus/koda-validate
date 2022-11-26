from typing import Any, Final, Literal, Tuple

from koda_validate.base import (
    InvalidType,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_BYTES_ERR: Final[Tuple[Literal[False], ValidationErr]] = (
    False,
    InvalidType(bytes, "expected a bytes object"),
)


class BytesValidator(_ToTupleValidatorUnsafeScalar[Any, str]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is bytes:
            return True, val
        else:
            return EXPECTED_BYTES_ERR
