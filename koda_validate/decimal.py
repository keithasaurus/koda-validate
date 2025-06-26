import decimal
from decimal import Decimal
from typing import Any

from koda import Just, Maybe, nothing

from koda_validate._internal import _ToTupleStandardValidator
from koda_validate.base import Predicate, PredicateAsync, Processor
from koda_validate.coerce import Coercer, coercer


@coercer(str, int, Decimal)
def coerce_decimal(val: Any) -> Maybe[Decimal]:
    if type(val) is Decimal:
        return Just(val)
    elif isinstance(val, (str, int)):
        try:
            return Just(Decimal(val))
        except decimal.InvalidOperation:
            pass

    return nothing


class DecimalValidator(_ToTupleStandardValidator[Decimal]):
    _TYPE = Decimal

    def __init__(
        self,
        *predicates: Predicate[Decimal],
        predicates_async: list[PredicateAsync[Decimal]] | None = None,
        preprocessors: list[Processor[Decimal]] | None = None,
        coerce: Coercer[Decimal] | None = coerce_decimal,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
