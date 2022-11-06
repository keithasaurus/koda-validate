from datetime import date, datetime
from typing import Any, Final, List, Optional

from koda_validate._internals import (
    _handle_scalar_processors_and_predicates,
    _handle_scalar_processors_and_predicates_async,
)
from koda_validate.typedefs import (
    Err,
    Predicate,
    PredicateAsync,
    Processor,
    Result,
    Serializable,
    Validator,
)

EXPECTED_DATE_ERR: Final[Err[Serializable]] = Err(
    ["expected date formatted as yyyy-mm-dd"]
)

EXPECTED_ISO_DATESTRING: Final[Err[Serializable]] = Err(
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

    def __call__(self, val: Any) -> Result[date, Serializable]:
        try:
            val = date.fromisoformat(val)
        except (ValueError, TypeError):
            return EXPECTED_DATE_ERR
        else:
            return _handle_scalar_processors_and_predicates(
                val, self.preprocessors, self.predicates
            )

    async def validate_async(self, val: Any) -> Result[date, Serializable]:
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

    def __call__(self, val: Any) -> Result[datetime, Serializable]:
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

    async def validate_async(self, val: Any) -> Result[datetime, Serializable]:
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
