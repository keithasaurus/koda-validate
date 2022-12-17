from typing import Any
from uuid import UUID

from koda_validate import CoercionErr, Invalid
from koda_validate._internal import ResultTuple, _CoercingValidator


class UUIDValidator(_CoercingValidator[UUID]):
    def coerce_to_type(self, val: Any) -> ResultTuple[UUID]:
        if type(val) is UUID:
            return True, val

        elif type(val) is str:
            try:
                return True, UUID(val)
            except ValueError:
                return False, Invalid(
                    CoercionErr(
                        {str, UUID},
                        UUID,
                    ),
                    val,
                    self,
                )

        else:
            return False, Invalid(
                CoercionErr(
                    {str, UUID},
                    UUID,
                ),
                val,
                self,
            )
