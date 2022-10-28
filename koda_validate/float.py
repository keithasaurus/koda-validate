from typing import Any, Final

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors

EXPECTED_FLOAT_ERR: Final[Err[Serializable]] = Err(["expected a float"])


class FloatValidator(Validator[Any, float, Serializable]):
    __slots__ = ("predicates",)
    __match_args__ = ("predicates",)

    def __init__(self, *predicates: Predicate[float, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            if len(self.predicates) == 0:
                return Ok(val)
            else:
                return accum_errors(val, self.predicates)
        else:
            return EXPECTED_FLOAT_ERR
