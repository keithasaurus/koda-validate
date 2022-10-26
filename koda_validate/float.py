from dataclasses import dataclass
from typing import Any, Tuple

from koda import Err, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors, expected


@dataclass(init=False)
class FloatValidator(Validator[Any, float, Serializable]):
    predicates: Tuple[Predicate[float, Serializable], ...]

    def __init__(self, *predicates: Predicate[float, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return accum_errors(val, self.predicates)
        else:
            return Err([expected("a float")])
