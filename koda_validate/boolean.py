from typing import Any, Final, List, Optional

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.base import (
    InvalidType,
    Predicate,
    PredicateAsync,
    Processor,
    ValidationErr,
    ValidationResult,
    Validator,
)
from koda_validate.validated import Invalid, Valid

EXPECTED_BOOL_ERR: Final[Invalid[ValidationErr]] = Invalid(
    InvalidType(bool, "expected a boolean")
)


class BoolValidator(Validator[Any, bool]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[bool],
        predicates_async: Optional[List[PredicateAsync[bool]]] = None,
        preprocessors: Optional[List[Processor[bool]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> ValidationResult[bool]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is bool:
            if self.preprocessors:
                for proc in self.preprocessors:
                    val = proc(val)

            if self.predicates:
                errors: ValidationErr = [
                    pred for pred in self.predicates if not pred(val)
                ]
                if errors:
                    return Invalid(errors)
                else:
                    return Valid(val)
            else:
                return Valid(val)
        else:
            return EXPECTED_BOOL_ERR

    async def validate_async(self, val: Any) -> ValidationResult[bool]:
        if type(val) is bool:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )
        else:
            return EXPECTED_BOOL_ERR
