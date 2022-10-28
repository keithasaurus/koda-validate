from dataclasses import dataclass
from typing import Any, Final, Tuple

from koda import Err, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors, expected

# extracted for optimization
EXPECTED_INTEGER_ERR: Final[Err[Serializable]] = Err([expected("an integer")])


class IntValidator(Validator[Any, int, Serializable]):
    __slots__ = ("predicates",)
    __match_args__ = ("predicates",)

    def __init__(self, *predicates: Predicate[int, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[int, Serializable]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors(val, self.predicates)
        else:
            return EXPECTED_INTEGER_ERR
