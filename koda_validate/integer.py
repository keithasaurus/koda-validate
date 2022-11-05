from typing import Any, Final, List, Optional

from koda import Err, Result

from koda_validate._internals import (
    ResultTuple,
    _FastValidator,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.typedefs import Predicate, PredicateAsync, Processor, Serializable

EXPECTED_INTEGER_MSG: Final[Serializable] = ["expected an integer"]
EXPECTED_INTEGER_ERR: Final[Err[Serializable]] = Err(EXPECTED_INTEGER_MSG)


class IntValidator(_FastValidator[Any, int, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[int, Serializable],
        predicates_async: Optional[List[PredicateAsync[int, Serializable]]] = None,
        preprocessors: Optional[List[Processor[int]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> ResultTuple[int, Serializable]:
        if type(val) is int:
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

        return False, EXPECTED_INTEGER_MSG

    async def validate_async(self, val: Any) -> Result[int, Serializable]:
        if type(val) is int:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_INTEGER_ERR
