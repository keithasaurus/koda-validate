import decimal
from decimal import Decimal as Decimal
from typing import Any, Final, Literal, Tuple

from koda_validate.base import (
    InvalidCoercion,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafeScalar,
)

EXPECTED_DECIMAL_ERR: Final[
    Tuple[Literal[False], ValidationErr]
] = False, InvalidCoercion(
    compatible_types=[str, int, Decimal],
    dest_type=Decimal,
    err_message="expected a Decimal, or a Decimal-compatible string or integer",
)


class DecimalValidator(_ToTupleValidatorUnsafeScalar[Any, Decimal]):
    def coerce_to_type(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is Decimal:
            return True, val
        elif isinstance(val, (str, int)):
            try:
                return True, Decimal(val)
            except decimal.InvalidOperation:
                return EXPECTED_DECIMAL_ERR
        else:
            return EXPECTED_DECIMAL_ERR
