import decimal
from decimal import Decimal as Decimal
from typing import Any, List, Optional

from koda import Just, Maybe, nothing

from koda_validate._internal import _ToTupleScalarValidator
from koda_validate.base import Coercer, Predicate, PredicateAsync, Processor


class CoerceDecimal(Coercer[Decimal]):
    compatible_types = {str, int, Decimal}

    def __call__(self, val: Any) -> Maybe[Decimal]:
        if type(val) is Decimal:
            return Just(val)
        elif isinstance(val, (str, int)):
            try:
                return Just(Decimal(val))
            except decimal.InvalidOperation:
                pass

        return nothing


class DecimalValidator(_ToTupleScalarValidator[Decimal]):
    _TYPE = Decimal

    def __init__(
        self,
        *predicates: Predicate[Decimal],
        predicates_async: Optional[List[PredicateAsync[Decimal]]] = None,
        preprocessors: Optional[List[Processor[Decimal]]] = None,
        coerce: Optional[Coercer[Decimal]] = CoerceDecimal(),
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
