from typing import Any
from uuid import UUID

from koda_validate._internal import _CoercingValidator, _ResultTuple
from koda_validate.errors import CoercionErr
from koda_validate.valid import Invalid


class UUIDValidator(_CoercingValidator[UUID]):
    def coerce_to_type(self, val: Any) -> _ResultTuple[UUID]:
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
