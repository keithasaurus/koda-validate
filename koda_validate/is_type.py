from typing import Optional, Type

from koda_validate import Predicate, PredicateAsync, Processor
from koda_validate._generics import SuccessT
from koda_validate._internal import _ToTupleStandardValidator
from koda_validate.coerce import Coercer


class TypeValidator(_ToTupleStandardValidator[SuccessT]):
    def __init__(
        self,
        type_: Type[SuccessT],
        *,
        predicates: list[Predicate[SuccessT]] | None = None,
        predicates_async: list[PredicateAsync[SuccessT]] | None = None,
        preprocessors: list[Processor[SuccessT]] | None = None,
        coerce: Coercer[SuccessT] | None = None,
    ) -> None:
        self._TYPE = type_
        super().__init__(
            *(predicates or []),
            predicates_async=predicates_async,
            preprocessors=preprocessors,
            coerce=coerce,
        )
