from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Tuple

from koda import Err, Ok, Result

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import expected


@dataclass(frozen=True, init=False)
class DateValidator(Validator[Any, date, JSONValue]):
    """
    Expects dates to be yyyy-mm-dd
    """

    predicates: Tuple[Predicate[date, JSONValue], ...]

    def __init__(self, *predicates: Predicate[date, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[date, JSONValue]:
        try:
            return Ok(date.fromisoformat(val))
        except (ValueError, TypeError):
            return Err(["expected date formatted as yyyy-mm-dd"])


@dataclass(frozen=True, init=False)
class DatetimeValidator(Validator[Any, date, JSONValue]):
    predicates: Tuple[Predicate[date, JSONValue], ...]

    def __init__(self, *predicates: Predicate[date, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[date, JSONValue]:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            return Ok(datetime.fromisoformat(val))
        except (ValueError, TypeError):
            return Err([expected("iso8601-formatted string")])
