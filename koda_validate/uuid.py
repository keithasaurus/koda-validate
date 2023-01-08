from typing import Any, Callable, List, Optional, Set, Type
from uuid import UUID

from koda import Err, Ok, Result

from koda_validate import Predicate, PredicateAsync, Processor
from koda_validate._internal import _ToTupleScalarValidator


def coerce_to_uuid(val: Any) -> Result[UUID, Set[Type[Any]]]:
    if type(val) is UUID:
        return Ok(val)

    elif type(val) is str:
        try:
            return Ok(UUID(val))
        except ValueError:
            pass

    return Err({str, UUID})


class UUIDValidator(_ToTupleScalarValidator[UUID]):
    _TYPE = UUID

    def __init__(
        self,
        *predicates: Predicate[UUID],
        predicates_async: Optional[List[PredicateAsync[UUID]]] = None,
        preprocessors: Optional[List[Processor[UUID]]] = None,
        coerce_to_type: Optional[
            Callable[[Any], Result[UUID, Set[Type[Any]]]]
        ] = coerce_to_uuid,
    ) -> None:
        super().__init__(
            *predicates,
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce_to_type=coerce_to_type,
        )
