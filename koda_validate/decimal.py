import decimal
from decimal import Decimal as Decimal
from typing import Any, Final, List, Literal, Optional, Tuple

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates_async_tuple,
    _handle_scalar_processors_and_predicates_tuple,
)
from koda_validate.base import (
    CoercionErr,
    Predicate,
    PredicateAsync,
    Processor,
    TypeErr,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)

EXPECTED_DECIMAL_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, [
    TypeErr(
        compatible_types=[str, int, Decimal],
        default_message="expected a Decimal, or a Decimal-compatible string or integer",
    )
]


class DecimalValidator(_ToTupleValidatorUnsafe[Any, Decimal]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[Decimal],
        predicates_async: Optional[List[PredicateAsync[Decimal]]] = None,
        preprocessors: Optional[List[Processor[Decimal]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is Decimal:
            return _handle_scalar_processors_and_predicates_tuple(
                val, self.preprocessors, self.predicates
            )

        elif isinstance(val, (str, int)):
            try:
                dec = Decimal(val)
            except decimal.InvalidOperation:
                return EXPECTED_DECIMAL_ERR
            else:
                return _handle_scalar_processors_and_predicates_tuple(
                    dec, self.preprocessors, self.predicates
                )

        else:
            return EXPECTED_DECIMAL_ERR

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is Decimal:
            return await _handle_scalar_processors_and_predicates_async_tuple(
                val, self.preprocessors, self.predicates, self.predicates_async
            )

        elif isinstance(val, (str, int)):
            try:
                dec = Decimal(val)
            except decimal.InvalidOperation:
                return EXPECTED_DECIMAL_ERR
            else:
                return await _handle_scalar_processors_and_predicates_async_tuple(
                    dec, self.preprocessors, self.predicates, self.predicates_async
                )

        else:
            return EXPECTED_DECIMAL_ERR
