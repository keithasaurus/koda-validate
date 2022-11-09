from datetime import date, datetime
from typing import Any, Final, List, Optional

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)
from koda_validate.validated import Invalid, Validated

EXPECTED_DATE_ERR: Final[Invalid[Serializable]] = Invalid(
    ["expected date formatted as yyyy-mm-dd"]
)

EXPECTED_ISO_DATESTRING: Final[Invalid[Serializable]] = Invalid(
    ["expected iso8601-formatted string"]
)


class DateStringValidator(Validator[Any, date, Serializable]):
    """
    Expects dates to be yyyy-mm-dd
    """

    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[date, Serializable],
        predicates_async: Optional[List[PredicateAsync[date, Serializable]]] = None,
        preprocessors: Optional[List[Processor[date]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Validated[date, Serializable]:
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

    async def validate_async(self, val: Any) -> Validated[date, Serializable]:
        try:
            val = date.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_DATE_ERR
        else:
            return await _handle_scalar_processors_and_predicates_async(
                val, self.preprocessors, self.predicates, self.predicates_async
            )


class DatetimeStringValidator(Validator[Any, datetime, Serializable]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[datetime, Serializable],
        predicates_async: Optional[List[PredicateAsync[datetime, Serializable]]] = None,
        preprocessors: Optional[List[Processor[datetime]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def __call__(self, val: Any) -> Validated[datetime, Serializable]:
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

    async def validate_async(self, val: Any) -> Validated[datetime, Serializable]:
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
