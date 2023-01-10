from datetime import date, datetime
from typing import Any, Callable, List, Optional, Set, Type

from koda import Err, Just, Maybe, Ok, Result, nothing

from koda_validate import Predicate, PredicateAsync, Processor
from koda_validate._internal import _ToTupleScalarValidator
from koda_validate.base import Coercer


class CoerceDate(Coercer[date]):
    compatible_types = {str, date}

    def __call__(self, val: Any) -> Maybe[date]:
        if type(val) is date:
            return Just(val)
        else:
            try:
                return Just(date.fromisoformat(val))
            except (ValueError, TypeError):
                return nothing


class DateValidator(_ToTupleScalarValidator[date]):
    _TYPE = date

    def __init__(
        self,
        *predicates: Predicate[date],
        predicates_async: Optional[List[PredicateAsync[date]]] = None,
        preprocessors: Optional[List[Processor[date]]] = None,
        coerce: Optional[Coercer[date]] = CoerceDate(),
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )


def coerce_datetime(val: Any) -> Result[datetime, Set[Type[Any]]]:
    if type(val) is datetime:
        return Ok(val)
    else:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            return Ok(datetime.fromisoformat(val))
        except (ValueError, TypeError):
            return Err({str, datetime})


class CoerceDatetime(Coercer[date]):
    compatible_types = {str, date}

    def __call__(self, val: Any) -> Maybe[date]:
        if type(val) is date:
            return Just(val)
        else:
            try:
                return Just(date.fromisoformat(val))
            except (ValueError, TypeError):
                return nothing


class DatetimeValidator(_ToTupleScalarValidator[datetime]):
    _TYPE = datetime

    def __init__(
        self,
        *predicates: Predicate[datetime],
        predicates_async: Optional[List[PredicateAsync[datetime]]] = None,
        preprocessors: Optional[List[Processor[datetime]]] = None,
        coerce: Optional[
            Callable[[Any], Result[datetime, Set[Type[Any]]]]
        ] = coerce_datetime,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
