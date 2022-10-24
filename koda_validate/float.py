from dataclasses import dataclass
from typing import Any, Tuple

from koda import Err, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors_serializable, expected


@dataclass(init=False, frozen=True)
class FloatValidator(Validator[Any, float, Serializable]):
    predicates: Tuple[Predicate[float, Serializable], ...]

    def __init__(self, *predicates: Predicate[float, Serializable]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return accum_errors_serializable(val, self.predicates)
        else:
            return Err([expected("a float")])
