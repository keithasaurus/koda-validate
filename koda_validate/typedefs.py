from abc import abstractmethod
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    final,
)

from koda_validate._generics import A, B, FailT


class Ok(Generic[A]):
    __match_args__ = ("val",)
    __slots__ = ("val",)

    is_ok: ClassVar[Literal[True]] = True

    def __init__(self, val: A) -> None:
        self.val: A = val

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ok) and other.val == self.val

    def __repr__(self) -> str:
        return f"Ok({repr(self.val)})"

    def apply(self, container: "Result[Callable[[A], B], FailT]") -> "Result[B, FailT]":
        if isinstance(container, Ok):
            return Ok(container.val(self.val))
        else:
            return container

    def get_or_else(self, _: A) -> A:
        return self.val

    def flat_map(self, fn: Callable[[A], "Result[B, FailT]"]) -> "Result[B, FailT]":
        return fn(self.val)

    def flat_map_err(self, fn: Callable[[Any], "Result[A, B]"]) -> "Result[A, B]":
        return self

    def map(self, fn: Callable[[A], B]) -> "Result[B, FailT]":
        return Ok(fn(self.val))

    def map_err(self, fn: Callable[[Any], "B"]) -> "Result[A, B]":
        return self

    def swap(self) -> "Result[FailT, A]":
        return Err(self.val)

    @property
    def to_optional(self) -> Optional[A]:
        """
        Note that `Ok[None]` will return None!
        """
        return self.val

    @property
    def to_maybe(self) -> "Maybe[A]":
        from koda.maybe import Just

        return Just(self.val)


class Err(Generic[FailT]):
    __match_args__ = ("val",)
    __slots__ = ("val",)

    is_ok: ClassVar[Literal[False]] = False

    def __init__(self, val: FailT) -> None:
        self.val: FailT = val

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Err) and other.val == self.val

    def __repr__(self) -> str:
        return f"Err({repr(self.val)})"

    def apply(self, _: "Result[Callable[[Any], B], FailT]") -> "Result[B, FailT]":
        return self

    def get_or_else(self, fallback: A) -> A:
        return fallback

    def map(self, _: Callable[[Any], B]) -> "Result[B, FailT]":
        return self

    def flat_map(self, _: Callable[[Any], "Result[B, FailT]"]) -> "Result[B, FailT]":
        return self

    def flat_map_err(self, fn: Callable[[FailT], "Result[A, B]"]) -> "Result[A, B]":
        return fn(self.val)

    def map_err(self, fn: Callable[[FailT], B]) -> "Result[A, B]":
        return Err(fn(self.val))

    def swap(self) -> "Result[FailT, A]":
        return Ok(self.val)

    @property
    def to_optional(self) -> Optional[Any]:
        return None

    @property
    def to_maybe(self) -> "Maybe[Any]":
        from koda.maybe import nothing

        return nothing


Result = Union[Ok[A], Err[FailT]]


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
