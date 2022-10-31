import decimal
from decimal import Decimal as Decimal
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

EXPECTED_DECIMAL_ERR: Final[Err[Serializable]] = Err(
    ["expected a Decimal, or a Decimal-compatible string or integer"]
)


class DecimalValidator(Validator[Any, Decimal, Serializable]):
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

    def __call__(self, val: Any) -> Result[Decimal, Serializable]:
        if isinstance(val, Decimal):
            return _handle_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )

        elif isinstance(val, (str, int)):
            try:
                dec = Decimal(val)
            except decimal.InvalidOperation:
                return EXPECTED_DECIMAL_ERR
            else:
                return _handle_processors_and_predicates(
                    dec, self.preprocessors, self.predicates
                )

        else:
            return EXPECTED_DECIMAL_ERR

    async def validate_async(self, val: Any) -> Result[Decimal, Serializable]:
        if isinstance(val, Decimal):
            return await _handle_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )

        elif isinstance(val, (str, int)):
            try:
                dec = Decimal(val)
            except decimal.InvalidOperation:
                return EXPECTED_DECIMAL_ERR
            else:
                return await _handle_processors_and_predicates_async(
                    dec, self.preprocessors, self.predicates, self.predicates_async
                )

        else:
            return EXPECTED_DECIMAL_ERR
