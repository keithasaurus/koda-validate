from typing import Any, Final, List, Optional

from koda import Err, Result

from koda_validate._internals import (
    _handle_scalar_processors_and_predicates,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)

EXPECTED_BOOL_ERR: Final[Err[Serializable]] = Err(["expected a boolean"])


class BoolValidator(Validator[Any, bool, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[bool, Serializable],
        predicates_async: Optional[List[PredicateAsync[bool, Serializable]]] = None,
        preprocessors: Optional[List[Processor[bool]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Result[bool, Serializable]:
        if isinstance(val, bool):
            return _handle_scalar_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )
        else:
            return EXPECTED_BOOL_ERR

    async def validate_async(self, val: Any) -> Result[bool, Serializable]:
        if isinstance(val, bool):
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_BOOL_ERR
