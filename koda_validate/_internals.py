from typing import Callable, ClassVar, Final, List, Optional, Tuple

from koda import Err, Ok, Result

from koda_validate._generics import A, FailT
from koda_validate.typedefs import Predicate, PredicateAsync, Processor, Serializable


def _variant_errors(*variants: Serializable) -> Serializable:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Result[A, FailT]]],
    r: Result[A, FailT],
) -> Result[A, FailT]:
    if fn is None:
        return r
    else:
        if not r.is_ok:
            return r
        else:
            return fn(r.val)


OBJECT_ERRORS_FIELD: Final[str] = "__container__"


def _handle_scalar_predicates(
    predicates: Tuple[Predicate[A, Serializable], ...], val: A
) -> Result[A, Serializable]:
    errors = [result.val for pred in predicates if not (result := pred(val)).is_ok]
    if errors:
        return Err(errors)
    else:
        return Ok(val)


def _handle_scalar_processors_and_predicates(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
) -> Result[A, Serializable]:
    if preprocessors is not None:
        for proc in preprocessors:
            val = proc(val)

    if predicates:
        errors = [result.val for pred in predicates if not (result := pred(val)).is_ok]
        if errors:
            return Err(errors)
        else:
            # has to be original val because there are no
            # errors, and predicates prevent there from being
            # modification to the value
            return Ok(val)
    else:
        return Ok(val)


async def _handle_scalar_processors_and_predicates_async(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
    predicates_async: Optional[List[PredicateAsync[A, Serializable]]],
) -> Result[A, Serializable]:
    if preprocessors is not None:
        for proc in preprocessors:
            val = proc(val)

    errors = [result.val for pred in predicates if not (result := pred(val)).is_ok]

    if predicates_async:
        errors.extend(
            [
                result.val
                for pred in predicates_async
                if not (result := await pred.validate_async(val)).is_ok
            ]
        )
    if errors:
        return Err(errors)
    else:
        # has to be original val because there are no
        # errors, and predicates prevent there from being
        # modification to the value
        return Ok(val)


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
