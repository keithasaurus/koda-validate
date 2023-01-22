from typing import Any, List, Optional
from uuid import UUID

from koda import Just, Maybe, nothing

from koda_validate import Predicate, PredicateAsync, Processor
from koda_validate._internal import _ToTupleStandardValidator
from koda_validate.coerce import Coercer, coercer


@coercer(str, UUID)
def coerce_uuid(val: Any) -> Maybe[UUID]:
    if type(val) is UUID:
        return Just(val)

    elif type(val) is str:
        try:
            return Just(UUID(val))
        except ValueError:
            pass

    return nothing


class UUIDValidator(_ToTupleStandardValidator[UUID]):
    _TYPE = UUID

    def __init__(
        self,
        *predicates: Predicate[UUID],
        predicates_async: Optional[List[PredicateAsync[UUID]]] = None,
        preprocessors: Optional[List[Processor[UUID]]] = None,
        coerce: Optional[Coercer[UUID]] = coerce_uuid,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
