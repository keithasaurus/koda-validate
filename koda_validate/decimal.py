import decimal
from dataclasses import dataclass
from decimal import Decimal as Decimal
from typing import Any, Tuple

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import expected


@dataclass(init=False, frozen=True)
class DecimalValidator(Validator[Any, Decimal, Serializable]):
    predicates: Tuple[Predicate[Decimal, Serializable], ...]

    def __init__(self, *predicates: Predicate[Decimal, Serializable]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[Decimal, Serializable]:
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
