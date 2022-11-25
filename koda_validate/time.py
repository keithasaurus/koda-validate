from datetime import date, datetime
from typing import Any, Final, List, Literal, Optional, Tuple

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates_async_tuple,
    _handle_scalar_processors_and_predicates_tuple,
)
from koda_validate.base import (
    InvalidCoercion,
    Predicate,
    PredicateAsync,
    Processor,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)

EXPECTED_DATE_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, InvalidCoercion(
    [str], date, "expected date formatted as yyyy-mm-dd"
)

EXPECTED_ISO_DATESTRING: Final[
    Tuple[Literal[False], ValidationErr]
] = False, InvalidCoercion([str], datetime, "expected iso8601-formatted string")


class DateStringValidator(_ToTupleValidatorUnsafe[Any, date]):
    """
    Expects dates to be yyyy-mm-dd
    """

    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[date],
        predicates_async: Optional[List[PredicateAsync[date]]] = None,
        preprocessors: Optional[List[Processor[date]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        try:
            val = date.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_DATE_ERR
        else:
            return _handle_scalar_processors_and_predicates_tuple(
                val, self.preprocessors, self.predicates
            )

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        try:
            val = date.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_DATE_ERR
        else:
            return await _handle_scalar_processors_and_predicates_async_tuple(
                val, self.preprocessors, self.predicates, self.predicates_async
            )


class DatetimeStringValidator(_ToTupleValidatorUnsafe[Any, datetime]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[datetime],
        predicates_async: Optional[List[PredicateAsync[datetime]]] = None,
        preprocessors: Optional[List[Processor[datetime]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            val_ = datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_ISO_DATESTRING
        else:
            return _handle_scalar_processors_and_predicates_tuple(
                val_, self.preprocessors, self.predicates
            )

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            val_ = datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_ISO_DATESTRING
        else:
            return await _handle_scalar_processors_and_predicates_async_tuple(
                val_, self.preprocessors, self.predicates, self.predicates_async
            )
