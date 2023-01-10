from typing import Any, Callable, List, Optional, Set, Type
from uuid import UUID

from koda import Err, Just, Maybe, Ok, Result, nothing

from koda_validate import Predicate, PredicateAsync, Processor
from koda_validate._internal import _ToTupleScalarValidator
from koda_validate.base import Coercer


class CoerceUUID(Coercer[UUID]):
    compatible_types = {str, UUID}

    def __call__(self, val: Any) -> Maybe[UUID]:
        if type(val) is UUID:
            return Just(val)

        elif type(val) is str:
            try:
                return Just(UUID(val))
            except ValueError:
                pass

        return nothing


class UUIDValidator(_ToTupleScalarValidator[UUID]):
    _TYPE = UUID

    def __init__(
        self,
        *predicates: Predicate[UUID],
        predicates_async: Optional[List[PredicateAsync[UUID]]] = None,
        preprocessors: Optional[List[Processor[UUID]]] = None,
        coerce: Optional[Coercer[UUID]] = CoerceUUID(),
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
