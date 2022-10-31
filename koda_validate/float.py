from typing import Any, Final, List, Optional

from koda import Err, Result

from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)
from koda_validate.utils import (
    _handle_processors_and_predicates,
    _handle_processors_and_predicates_async,
)

EXPECTED_FLOAT_ERR: Final[Err[Serializable]] = Err(["expected a float"])


class FloatValidator(Validator[Any, float, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[float, Serializable],
        predicates_async: Optional[List[PredicateAsync[float, Serializable]]] = None,
        preprocessors: Optional[List[Processor[float]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return _handle_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )
        return EXPECTED_FLOAT_ERR

    async def validate_async(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return await _handle_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_FLOAT_ERR
