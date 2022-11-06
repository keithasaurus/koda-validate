from typing import Any, Final, List, Optional

from koda_validate._internals import _handle_scalar_processors_and_predicates_async
from koda_validate.typedefs import (
    Invalid,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Valid,
    Validated,
    Validator,
)

# extracted for optimization
EXPECTED_INTEGER_ERR: Final[Invalid[Serializable]] = Invalid(["expected an integer"])


class IntValidator(Validator[Any, int, Serializable]):
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

    def __call__(self, val: Any) -> Validated[int, Serializable]:
        if type(val) is int:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                if errors := [
                    pred.err(val) for pred in self.predicates if not pred.is_valid(val)
                ]:
                    return Invalid(errors)
                else:
                    return Valid(val)
            else:
                return Valid(val)

        return EXPECTED_INTEGER_ERR

    async def validate_async(self, val: Any) -> Validated[int, Serializable]:
        if type(val) is int:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_INTEGER_ERR
