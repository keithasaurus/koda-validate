from abc import abstractmethod
from typing import Any, Dict, Generic, List, Literal, Tuple, Union, final

from koda import Err, Ok, Result

from koda_validate._generics import A, B, FailT


class Validator(Generic[A, B, FailT]):
    """
    Essentially a `Callable[[A], Result[B, FailT]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    def __call__(self, val: A) -> Result[B, FailT]:  # pragma: no cover
        raise NotImplementedError

    async def validate_async(self, val: A) -> Result[B, FailT]:  # pragma: no cover
        """
        make it possible for all validators to be async-compatible
        """
        raise NotImplementedError


class Predicate(Generic[A, FailT]):
    """
    The important aspect of a `Predicate` is that it is not
    possible to change the data passed in (it is technically possible to mutate
    mutable values in the course of json, but that is considered an
    error in the opinion of this library).

    Compatible with Async / but async behavior is _not_ customizable. that's
    why we have PredicateAsync. Any IO needs should probably go there!
    """

    @abstractmethod
    def is_valid(self, val: A) -> bool:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def err(self, val: A) -> FailT:  # pragma: no cover
        raise NotImplementedError

    @final
    def __call__(self, val: A) -> Result[A, FailT]:
        if self.is_valid(val) is True:
            return Ok(val)
        else:
            return Err(self.err(val))


class PredicateAsync(Generic[A, FailT]):
    """
    For async-only validation.
    """

    @abstractmethod
    async def is_valid_async(self, val: A) -> bool:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    async def err_async(self, val: A) -> FailT:  # pragma: no cover
        raise NotImplementedError

    @final
    async def validate_async(self, val: A) -> Result[A, FailT]:
        if await self.is_valid_async(val) is True:
            return Ok(val)
        else:
            return Err(await self.err_async(val))


# When mypy enables recursive types by default
# Serializable = Union[
#    None, int, str, bool, float,
#    List["Serializable"], Tuple["Serializable", ...], Dict[str, "Serializable"]
# ]
Serializable1 = Union[
    None, int, str, bool, float, List[Any], Tuple[Any, ...], Dict[str, Any]
]
Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    List[Serializable1],
    Tuple[Serializable1, ...],
    Dict[str, Serializable1],
]


class Processor(Generic[A]):
    @abstractmethod
    def __call__(self, val: A) -> A:  # pragma: no cover
        raise NotImplementedError


_ResultTuple = Union[Tuple[Literal[True], A], Tuple[Literal[False], FailT]]


class _ToTupleValidator(Validator[A, B, FailT]):
    """
    This validator exists for optimization. When we call
    nested validators it's much less computation to deal with simple
    tuples and bools, instead of Ok and Err instances.

    This class may go away!
    """

    def validate_to_tuple(self, val: A) -> _ResultTuple[A, FailT]:
        raise NotImplementedError

    def __call__(self, val: A) -> Result[A, FailT]:
        valid, result_val = self.validate_to_tuple(val)
        if valid:
            return Ok(result_val)
        else:
            return Err(result_val)

    async def validate_to_tuple_async(self, val: A) -> _ResultTuple[A, FailT]:
        raise NotImplementedError

    async def validate_async(self, val: A) -> Result[A, FailT]:
        valid, result_val = await self.validate_to_tuple_async(val)
        if valid:
            return Ok(result_val)
        else:
            return Err(result_val)
