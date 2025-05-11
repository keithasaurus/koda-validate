from datetime import date, datetime
from typing import Any, Optional

from koda import Just, Maybe, nothing

from koda_validate import Predicate, PredicateAsync, Processor
from koda_validate._internal import _ToTupleStandardValidator
from koda_validate.coerce import Coercer, coercer


@coercer(str, date)
def coerce_date(val: Any) -> Maybe[date]:
    if type(val) is date:
        return Just(val)
    else:
        try:
            return Just(date.fromisoformat(val))
        except (ValueError, TypeError):
            return nothing


class DateValidator(_ToTupleStandardValidator[date]):
    _TYPE = date

    def __init__(
        self,
        *predicates: Predicate[date],
        predicates_async: Optional[list[PredicateAsync[date]]] = None,
        preprocessors: Optional[list[Processor[date]]] = None,
        coerce: Optional[Coercer[date]] = coerce_date,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )


@coercer(str, datetime)
def coerce_datetime(val: Any) -> Maybe[datetime]:
    if type(val) is datetime:
        return Just(val)
    else:
        try:
            return Just(datetime.fromisoformat(val))
        except (ValueError, TypeError):
            return nothing


class DatetimeValidator(_ToTupleStandardValidator[datetime]):
    _TYPE = datetime

    def __init__(
        self,
        *predicates: Predicate[datetime],
        predicates_async: Optional[list[PredicateAsync[datetime]]] = None,
        preprocessors: Optional[list[Processor[datetime]]] = None,
        coerce: Optional[Coercer[datetime]] = coerce_datetime,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
