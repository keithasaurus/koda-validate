from typing import Any, Final, Literal, Tuple
from uuid import UUID

from koda_validate.base import (
    InvalidCoercion,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_UUID_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, InvalidCoercion(
    [str, UUID], UUID, "expected a UUID, or a UUID-compatible string"
)


class UUIDValidator(_ToTupleValidatorUnsafeScalar[Any, UUID]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is UUID:
            return True, val

        elif type(val) is str:
            try:
                return True, UUID(val)
            except ValueError:
                return EXPECTED_UUID_ERR
        else:
            return EXPECTED_UUID_ERR
