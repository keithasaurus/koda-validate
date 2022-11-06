from typing import Any, Final, List, Optional

from koda import Err, Ok, Result

from koda_validate._internals import _handle_scalar_processors_and_predicates_async
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
    _ResultTuple,
    _ToTupleValidator,
)

EXPECTED_BOOL_ERR: Final[Serializable] = ["expected a boolean"]


class BoolValidator(_ToTupleValidator[Any, bool, Serializable]):
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

    def validate_to_tuple(self, val: Any) -> _ResultTuple[bool, Serializable]:
        if type(val) is bool:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                if errors := [
                    pred.err(val) for pred in self.predicates if not pred.is_valid(val)
                ]:
                    return False, errors
                else:
                    return True, val
            else:
                return True, val
        else:
            return False, EXPECTED_BOOL_ERR

    async def validate_to_tuple_async(self, val: Any) -> _ResultTuple[bool, Serializable]:
        if type(val) is bool:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return False, EXPECTED_BOOL_ERR
