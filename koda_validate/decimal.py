import decimal
from decimal import Decimal as Decimal
from typing import Any, Final, List, Optional

from koda import Err

from koda_validate._internals import (
    _handle_scalar_processors_and_predicates,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    _ResultTuple,
    _ToTupleValidator,
)

EXPECTED_DECIMAL_MSG: Final[Serializable] = [
    "expected a Decimal, or a Decimal-compatible string or integer"
]
EXPECTED_DECIMAL_ERR: Final[Err[Serializable]] = Err(EXPECTED_DECIMAL_MSG)


class DecimalValidator(_ToTupleValidator[Any, Decimal, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[Decimal, Serializable],
        predicates_async: Optional[List[PredicateAsync[Decimal, Serializable]]] = None,
        preprocessors: Optional[List[Processor[Decimal]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> _ResultTuple[Decimal, Serializable]:
        if type(val) is Decimal:
            return _handle_scalar_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )

        elif isinstance(val, (str, int)):
            try:
                dec = Decimal(val)
            except decimal.InvalidOperation:
                return False, EXPECTED_DECIMAL_MSG
            else:
                return _handle_scalar_processors_and_predicates(
                    dec, self.preprocessors, self.predicates
                )

        else:
            return False, EXPECTED_DECIMAL_MSG

    async def validate_to_tuple_async(
        self, val: Any
    ) -> _ResultTuple[Decimal, Serializable]:
        if type(val) is Decimal:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )

        elif isinstance(val, (str, int)):
            try:
                dec = Decimal(val)
            except decimal.InvalidOperation:
                return False, EXPECTED_DECIMAL_MSG
            else:
                return await _handle_scalar_processors_and_predicates_async(
                    dec, self.preprocessors, self.predicates, self.predicates_async
                )

        else:
            return False, EXPECTED_DECIMAL_MSG
