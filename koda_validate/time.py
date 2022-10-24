from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Tuple

from koda import Err, Ok, Result

from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import expected


@dataclass(frozen=True, init=False)
class DateValidator(Validator[Any, date, Serializable]):
    """
    Expects dates to be yyyy-mm-dd
    """

    predicates: Tuple[Predicate[date, Serializable], ...]

    def __init__(self, *predicates: Predicate[date, Serializable]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[date, Serializable]:
        try:
            return Ok(date.fromisoformat(val))
        except (ValueError, TypeError):
            return Err(["expected date formatted as yyyy-mm-dd"])


@dataclass(frozen=True, init=False)
class DatetimeValidator(Validator[Any, date, Serializable]):
    predicates: Tuple[Predicate[date, Serializable], ...]

    def __init__(self, *predicates: Predicate[date, Serializable]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[date, Serializable]:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            return Ok(datetime.fromisoformat(val))
        except (ValueError, TypeError):
            return Err([expected("iso8601-formatted string")])
