from dataclasses import dataclass
from typing import Any, Tuple

from koda import Err, Result

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import accum_errors_json, expected


@dataclass(init=False, frozen=True)
class IntValidator(Validator[Any, int, JSONValue]):
    predicates: Tuple[Predicate[int, JSONValue]]

    def __init__(self, *predicates: Predicate[int, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[int, JSONValue]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors_json(val, self.predicates)
        else:
            return Err([expected("an integer")])
