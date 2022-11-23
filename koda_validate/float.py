from typing import Any, Final, List, Literal, Optional, Tuple

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates_async_tuple,
)
from koda_validate.base import (
    InvalidType,
    Predicate,
    PredicateAsync,
    Processor,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)

EXPECTED_FLOAT_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, (
    InvalidType(float, "expected a float")
)


class FloatValidator(_ToTupleValidatorUnsafe[Any, float]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[float],
        predicates_async: Optional[List[PredicateAsync[float]]] = None,
        preprocessors: Optional[List[Processor[float]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is float:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                if errors := [pred for pred in self.predicates if not pred.__call__(val)]:
                    return False, errors
                else:
                    return True, val
            else:
                return True, val

        return EXPECTED_FLOAT_ERR

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is float:
            return await _handle_scalar_processors_and_predicates_async_tuple(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_FLOAT_ERR
