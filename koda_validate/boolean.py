from dataclasses import dataclass
from typing import Any, Tuple

from koda import Err, Result

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import accum_errors_json, expected


@dataclass(init=False, frozen=True)
class BooleanValidator(Validator[Any, bool, JSONValue]):
    predicates: Tuple[Predicate[bool, JSONValue], ...]

    def __init__(self, *predicates: Predicate[bool, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[bool, JSONValue]:
        if isinstance(val, bool):
            return accum_errors_json(val, self.predicates)
        else:
            return Err([expected("a boolean")])
