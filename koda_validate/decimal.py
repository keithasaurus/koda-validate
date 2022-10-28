import decimal
from decimal import Decimal as Decimal
from typing import Any

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator


class DecimalValidator(Validator[Any, Decimal, Serializable]):
    def __init__(self, *predicates: Predicate[Decimal, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[Decimal, Serializable]:
        expected_msg = "expected a decimal-compatible string or integer"
        if isinstance(val, Decimal):
            return Ok(val)
        elif isinstance(val, (str, int)):
            try:
                return Ok(Decimal(val))
            except decimal.InvalidOperation:
                return Err([expected_msg])
        else:
            return Err([expected_msg])
