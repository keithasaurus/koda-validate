from datetime import date, datetime
from typing import Any

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator


class DateValidator(Validator[Any, date, Serializable]):
    """
    Expects dates to be yyyy-mm-dd
    """

    __slots__ = ("predicates",)
    __match_args__ = ("predicates",)

    def __init__(self, *predicates: Predicate[date, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[date, Serializable]:
        try:
            return Ok(date.fromisoformat(val))
        except (ValueError, TypeError):
            return Err(["expected date formatted as yyyy-mm-dd"])


class DatetimeValidator(Validator[Any, date, Serializable]):
    __slots__ = ("predicates",)
    __match_args__ = ("predicates",)

    def __init__(self, *predicates: Predicate[date, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[date, Serializable]:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            return Ok(datetime.fromisoformat(val))
        except (ValueError, TypeError):
            return Err(["expected iso8601-formatted string"])
