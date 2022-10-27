from dataclasses import dataclass
from typing import Any, Tuple

from koda import Err, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors, expected


@dataclass(init=False, frozen=True)
class IntValidator(Validator[Any, int, Serializable]):
    predicates: Tuple[Predicate[int, Serializable]]

    def __init__(self, *predicates: Predicate[int, Serializable]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[int, Serializable]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors(val, self.predicates)
        else:
            return Err([expected("an integer")])
