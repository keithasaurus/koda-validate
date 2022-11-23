from datetime import date, datetime
from typing import Any, Final, List, Optional

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.base import (
    CoercionErr,
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    ValidationErr,
    Validator,
)
from koda_validate.validated import Invalid, Validated

EXPECTED_DATE_ERR: Final[Invalid[ValidationErr]] = Invalid(
    CoercionErr([str], date, "expected date formatted as yyyy-mm-dd")
)

EXPECTED_ISO_DATESTRING: Final[Invalid[ValidationErr]] = Invalid(
    CoercionErr([str], datetime, "expected iso8601-formatted string")
)


class DateStringValidator(Validator[Any, date]):
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

    def __call__(self, val: Any) -> Validated[date, ValidationErr]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        try:
            val = date.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_DATE_ERR
        else:
            return _handle_scalar_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )

    async def validate_async(self, val: Any) -> Validated[date, ValidationErr]:
        try:
            val = date.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_DATE_ERR
        else:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )


class DatetimeStringValidator(Validator[Any, datetime]):
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

    def __call__(self, val: Any) -> Validated[datetime, ValidationErr]:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            val_ = datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_ISO_DATESTRING
        else:
            return _handle_scalar_processors_and_predicates(
                val_, self.preprocessors, self.predicates
            )

    async def validate_async(self, val: Any) -> Validated[datetime, ValidationErr]:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            val_ = datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_ISO_DATESTRING
        else:
            return await _handle_scalar_processors_and_predicates_async(
                val_, self.preprocessors, self.predicates, self.predicates_async
            )
