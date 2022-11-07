from typing import Any, Callable, ClassVar, Final, List, NoReturn, Optional, Tuple, Type

from koda_validate._generics import A, FailT
from koda_validate.base import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    _ResultTupleUnsafe,
)
from koda_validate.validated import Invalid, Valid, Validated


def _variant_errors(*variants: Serializable) -> Serializable:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


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


def _handle_scalar_processors_and_predicates(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
) -> Validated[A, Serializable]:
    if preprocessors is not None:
        for proc in preprocessors:
            val = proc(val)

    if predicates:
        if errors := [pred.err(val) for pred in predicates if not pred.is_valid(val)]:
            return Invalid(errors)
        else:
            return Valid(val)
    else:
        return Valid(val)


async def _handle_scalar_processors_and_predicates_async(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
    predicates_async: Optional[List[PredicateAsync[A, Serializable]]],
) -> Validated[A, Serializable]:
    if preprocessors:
        for proc in preprocessors:
            val = proc(val)

    errors = [pred.err(val) for pred in predicates if not pred.is_valid(val)]

    if predicates_async:
        errors.extend(
            [
                await pred.err_async(val)
                for pred in predicates_async
                if not await pred.is_valid_async(val)
            ]
        )
    if errors:
        return Invalid(errors)
    else:
        return Valid(val)


async def _handle_scalar_processors_and_predicates_async_tuple(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
    predicates_async: Optional[List[PredicateAsync[A, Serializable]]],
) -> _ResultTupleUnsafe:
    if preprocessors:
        for proc in preprocessors:
            val = proc(val)

    errors = [pred.err(val) for pred in predicates if not pred.is_valid(val)]

    if predicates_async:
        errors.extend(
            [
                await pred.err_async(val)
                for pred in predicates_async
                if not await pred.is_valid_async(val)
            ]
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
        f"Please remove the items in `predicates_async`, or call the `.validate_async` method instead."
    )
