from dataclasses import dataclass
from typing import Any, Tuple

from koda import Err, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import accum_errors


@dataclass(init=False, frozen=True)
class BooleanValidator(Validator[Any, bool, Serializable]):
    predicates: Tuple[Predicate[bool, Serializable], ...]

    def __init__(self, *predicates: Predicate[bool, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[bool, Serializable]:
        if isinstance(val, bool):
            if len(self.predicates) > 0:
                return
            return accum_errors(val, self.predicates)
        else:
            return Err([f"expected a boolean"])
