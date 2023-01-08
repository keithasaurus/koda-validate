import decimal
from decimal import Decimal as Decimal
from typing import Any, Callable, List, Optional, Set, Type

from koda import Err, Ok, Result

from koda_validate._internal import _ToTupleScalarValidator
from koda_validate.base import Predicate, PredicateAsync, Processor


def coerce_decimal(val: Any) -> Result[Decimal, Set[Type[Any]]]:
    if type(val) is Decimal:
        return Ok(val)
    elif isinstance(val, (str, int)):
        try:
            return Ok(Decimal(val))
        except decimal.InvalidOperation:
            pass

    return Err({str, int, Decimal})


class DecimalValidator(_ToTupleScalarValidator[Decimal]):
    _TYPE = Decimal

    def __init__(
        self,
        *predicates: Predicate[Decimal],
        predicates_async: Optional[List[PredicateAsync[Decimal]]] = None,
        preprocessors: Optional[List[Processor[Decimal]]] = None,
        coerce_to_type: Optional[
            Callable[[Any], Result[Decimal, Set[Type[Any]]]]
        ] = coerce_decimal,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce_to_type=coerce_to_type,
        )
