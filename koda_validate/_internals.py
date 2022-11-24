from typing import (
    Any,
    Callable,
    ClassVar,
    Final,
    List,
    NoReturn,
    Optional,
    Tuple,
    Type,
    Union,
)

from koda_validate._generics import A, FailT
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    ValidationErr,
    ValidationResult,
    _ResultTupleUnsafe,
)
from koda_validate.validated import Invalid, Valid, Validated


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Validated[A, FailT]]],
    r: Validated[A, FailT],
) -> Validated[A, FailT]:
    if fn is None:
        return r
    else:
        if not r.is_valid:
            return r
        else:
            return fn(r.val)


OBJECT_ERRORS_FIELD: Final[str] = "__container__"


def _handle_scalar_processors_and_predicates_tuple(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A], ...],
) -> _ResultTupleUnsafe:
    if preprocessors:
        for proc in preprocessors:
            val = proc(val)

    if predicates:
        if errors := [pred for pred in predicates if not pred(val)]:
            return False, errors
        else:
            return True, val
    else:
        return True, val


async def _handle_scalar_processors_and_predicates_async_tuple(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A], ...],
    predicates_async: Optional[List[PredicateAsync[A]]],
) -> _ResultTupleUnsafe:
    if preprocessors:
        for proc in preprocessors:
            val = proc(val)

    errors: List[Union[Predicate[A], PredicateAsync[A]]] = [
        pred for pred in predicates if not pred(val)
    ]

    if predicates_async:
        errors.extend(
            [pred for pred in predicates_async if not await pred.validate_async(val)]
        )
    if errors:
        return False, errors
    else:
        return True, val


class _NotSet:
    _instance: ClassVar[Optional["_NotSet"]] = None

    def __new__(cls) -> "_NotSet":
        """
        Make a singleton, so we can do `is` checks if we want.
        """
        if cls._instance is None:
            cls._instance = super(_NotSet, cls).__new__(cls)
        return cls._instance


_not_set = _NotSet()


def _async_predicates_warning(cls: Type[Any]) -> NoReturn:
    raise AssertionError(
        f"{cls.__name__} cannot run `predicates_async` in synchronous calls. "
        f"Please `await` the `.validate_async` method instead; or remove the "
        f"items in `predicates_async`."
    )
