from typing import Any, Final, List, Literal, Optional, Tuple
from uuid import UUID

from koda_validate._internals import (
    _async_predicates_warning,
    _handle_scalar_processors_and_predicates_async_tuple,
    _handle_scalar_processors_and_predicates_tuple,
)
from koda_validate.base import (
    InvalidCoercion,
    Predicate,
    PredicateAsync,
    Processor,
    ValidationErr,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)

EXPECTED_UUID_ERR: Final[Tuple[Literal[False], ValidationErr]] = False, InvalidCoercion(
    [str, UUID], UUID, "expected a UUID, or a UUID-compatible string"
)


class UUIDValidator(_ToTupleValidatorUnsafe[Any, UUID]):
    __match_args__ = ("predicates", "predicates_async", "preprocessors")
    __slots__ = ("predicates", "predicates_async", "preprocessors")

    def __init__(
        self,
        *predicates: Predicate[UUID],
        predicates_async: Optional[List[PredicateAsync[UUID]]] = None,
        preprocessors: Optional[List[Processor[UUID]]] = None,
    ) -> None:
        self.predicates = predicates
        self.predicates_async = predicates_async
        self.preprocessors = preprocessors

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if self.predicates_async:
            _async_predicates_warning(self.__class__)

        if type(val) is UUID:
            return _handle_scalar_processors_and_predicates_tuple(
                val, self.preprocessors, self.predicates
            )

        elif type(val) is str:
            try:
                _uuid = UUID(val)
            except ValueError:
                return EXPECTED_UUID_ERR
            else:
                return _handle_scalar_processors_and_predicates_tuple(
                    _uuid, self.preprocessors, self.predicates
                )
        else:
            return EXPECTED_UUID_ERR

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        if type(val) is UUID:
            return await _handle_scalar_processors_and_predicates_async_tuple(
                val, self.preprocessors, self.predicates, self.predicates_async
            )

        elif type(val) is str:
            try:
                _uuid = UUID(val)
            except ValueError:
                return EXPECTED_UUID_ERR
            else:
                return await _handle_scalar_processors_and_predicates_async_tuple(
                    _uuid, self.preprocessors, self.predicates, self.predicates_async
                )

        else:
            return EXPECTED_UUID_ERR
