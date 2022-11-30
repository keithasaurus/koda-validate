from typing import Any
from uuid import UUID

from koda_validate._internal import _CoercionValidator
from koda_validate.base import InvalidCoercion, _ResultTupleUnsafe


class UUIDValidator(_CoercionValidator[Any, UUID]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
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
