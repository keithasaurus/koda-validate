import decimal
from decimal import Decimal as Decimal
from typing import Any

from koda_validate._internal import _CoercingValidator, _ResultTuple
from koda_validate.errors import CoercionErr
from koda_validate.valid import Invalid


class DecimalValidator(_CoercingValidator[Decimal]):
    def coerce_to_type(self, val: Any) -> _ResultTuple[Decimal]:
        if type(val) is Decimal:
            return True, val
        elif isinstance(val, (str, int)):
            try:
                return True, Decimal(val)
            except decimal.InvalidOperation:
                pass

        return False, Invalid(
            CoercionErr(
                compatible_types={str, int, Decimal},
                dest_type=Decimal,
            ),
            val,
            self,
        )
