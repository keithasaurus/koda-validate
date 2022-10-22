import decimal
from dataclasses import dataclass
from decimal import Decimal as Decimal
from typing import Any, Tuple

from koda import Err, Ok, Result

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import expected


@dataclass(init=False, frozen=True)
class DecimalValidator(Validator[Any, Decimal, JSONValue]):
    predicates: Tuple[Predicate[Decimal, JSONValue], ...]

    def __init__(self, *predicates: Predicate[Decimal, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[Decimal, JSONValue]:
        expected_msg = expected("a decimal-compatible string or integer")
        if isinstance(val, Decimal):
            return Ok(val)
        elif isinstance(val, (str, int)):
            try:
                return Ok(Decimal(val))
            except decimal.InvalidOperation:
                return Err([expected_msg])
        else:
            return Err([expected_msg])
