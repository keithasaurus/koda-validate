from typing import Any

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors


class BooleanValidator(Validator[Any, bool, Serializable]):
    __slots__ = ("predicates",)

    def __init__(self, *predicates: Predicate[bool, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[bool, Serializable]:
        if isinstance(val, bool):
            if len(self.predicates) == 0:
                return Ok(val)
            return accum_errors(val, self.predicates)
        else:
            return Err([f"expected a boolean"])
