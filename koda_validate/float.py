from typing import Any

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors


class FloatValidator(Validator[Any, float, Serializable]):
    def __init__(self, *predicates: Predicate[float, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            if len(self.predicates) == 0:
                return Ok(val)
            else:
                return accum_errors(val, self.predicates)
        else:
            return Err([f"expected a float"])
