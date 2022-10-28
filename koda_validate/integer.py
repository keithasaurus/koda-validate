from typing import Any, Final

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors

# extracted for optimization
EXPECTED_INTEGER_ERR: Final[Err[Serializable]] = Err([f"expected an integer"])


class IntValidator(Validator[Any, int, Serializable]):
    __slots__ = ("predicates",)
    __match_args__ = ("predicates",)

    def __init__(self, *predicates: Predicate[int, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[int, Serializable]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            if len(self.predicates) == 0:
                return Ok(val)
            else:
                return accum_errors(val, self.predicates)
        else:
            return EXPECTED_INTEGER_ERR
