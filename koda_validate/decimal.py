import decimal
from decimal import Decimal as Decimal
from typing import Any

from koda_validate.base import (
    InvalidCoercion,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)


class DecimalValidator(_ToTupleValidatorUnsafeScalar[Any, Decimal]):
    def check_and_or_coerce_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is Decimal:
            return True, val
        elif isinstance(val, (str, int)):
            try:
                return True, Decimal(val)
            except decimal.InvalidOperation:
                return False, InvalidCoercion(
                    self,
                    compatible_types=[str, int, Decimal],
                    dest_type=Decimal,
                )

        else:
            return False, InvalidCoercion(
                self,
                compatible_types=[str, int, Decimal],
                dest_type=Decimal,
            )
