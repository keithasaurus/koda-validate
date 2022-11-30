from typing import Any
from uuid import UUID

from koda_validate._internal import _CoercingValidator, _ResultTupleUnsafe
from koda_validate.base import InvalidCoercion


class UUIDValidator(_CoercingValidator[UUID]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is UUID:
            return True, val

        elif type(val) is str:
            try:
                return True, UUID(val)
            except ValueError:
                return False, InvalidCoercion(
                    [str, UUID],
                    UUID,
                )

        else:
            return False, InvalidCoercion(
                [str, UUID],
                UUID,
            )
