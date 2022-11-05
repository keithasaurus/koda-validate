from typing import Callable, ClassVar, Final, List, Literal, Optional, Tuple, Union

from koda import Err, Ok, Result
from koda._generics import B

from koda_validate._generics import A, FailT
from koda_validate.typedefs import (
    Predicate,
    PredicateAsync,
    Processor,
    Serializable,
    Validator,
)


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


def _handle_scalar_processors_and_predicates(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
) -> Result[A, Serializable]:
    if preprocessors is not None:
        for proc in preprocessors:
            val = proc(val)

    if predicates:
        if errors := [pred.err(val) for pred in predicates if not pred.is_valid(val)]:
            return Err(errors)
        else:
            return Ok(val)
    else:
        return Ok(val)


async def _handle_scalar_processors_and_predicates_async(
    val: A,
    preprocessors: Optional[List[Processor[A]]],
    predicates: Tuple[Predicate[A, Serializable], ...],
    predicates_async: Optional[List[PredicateAsync[A, Serializable]]],
) -> Result[A, Serializable]:
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
        return Err(errors)
    else:
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

ResultTuple = Union[Tuple[Literal[True], A], Tuple[Literal[False], FailT]]


class _FastValidator(Validator[A, B, FailT]):
    """
    This validator exists for optimization. When we call
    nested validators it's much less computation to deal with simple
    tuples and bools, instead of Ok and Err instances.

    This class may go away!
    """

    def validate_to_tuple(self, val: A) -> ResultTuple[A, FailT]:
        raise NotImplementedError

    def __call__(self, val: A) -> Result[A, FailT]:
        valid, result_val = self.validate_to_tuple(val)
        if valid:
            return Ok(result_val)
        else:
            return Err(result_val)

    async def validate_to_tuple_async(self, val: A) -> ResultTuple[A, FailT]:
        raise NotImplementedError

    async def validate_async(self, val: A) -> Result[A, FailT]:
        valid, result_val = await self.validate_to_tuple_async(val)
        if valid:
            return Ok(result_val)
        else:
            return Err(result_val)
