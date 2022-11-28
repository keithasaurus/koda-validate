from typing import Any
from uuid import UUID

from koda_validate.base import (
    InvalidCoercion,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)


class UUIDValidator(_ToTupleValidatorUnsafeScalar[Any, UUID]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is UUID:
            return True, val

        elif type(val) is str:
            try:
                return True, UUID(val)
            except ValueError:
                return False, InvalidCoercion(
                    self,
                    [str, UUID],
                    UUID,
                )

        else:
            return False, InvalidCoercion(
                self,
                [str, UUID],
                UUID,
            )
