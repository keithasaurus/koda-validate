import decimal
from decimal import Decimal
from typing import Any, List, Optional

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
        predicates_async: Optional[List[PredicateAsync[Decimal]]] = None,
        preprocessors: Optional[List[Processor[Decimal]]] = None,
        coerce: Optional[Coercer[Decimal]] = coerce_decimal,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
