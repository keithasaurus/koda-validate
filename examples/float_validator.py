from typing import Any

from koda import Err, Result

from koda_validate import JSONValue, Predicate, Validator
from koda_validate.utils import accum_errors_json


class FloatValidator(Validator[Any, float, JSONValue]):
    def __init__(self, *predicates: Predicate[float, JSONValue]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return accum_errors_json(val, self.predicates)
        else:
            return Err(["expected a float"])
