from abc import abstractmethod
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Literal,
    Tuple,
    Union,
    final,
)

from koda import Ok, Result

from koda_validate._generics import A, B, FailT


class Valid(Generic[A]):
    __match_args__ = ("val",)
    __slots__ = ("val",)

    is_valid: ClassVar[Literal[True]] = True

    def __init__(self, val: A) -> None:
        self.val: A = val

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Valid) and other.val == self.val

    def __repr__(self) -> str:
        return f"Valid({repr(self.val)})"

    def flat_map(self, fn: Callable[[A], "Validated[B, FailT]"]) -> "Validated[B, FailT]":
        return fn(self.val)

    def flat_map_err(self, fn: Callable[[Any], "Validated[A, B]"]) -> "Validated[A, B]":
        return self

    def map(self, fn: Callable[[A], B]) -> "Validated[B, FailT]":
        return Valid(fn(self.val))

    def map_err(self, fn: Callable[[Any], "B"]) -> "Validated[A, B]":
        return self

    @property
    def as_result(self) -> Result[A, Any]:
        return Ok(self.val)


class Invalid(Generic[FailT]):
    __match_args__ = ("val",)
    __slots__ = ("val",)

    is_valid: ClassVar[Literal[False]] = False

    def __init__(self, val: FailT) -> None:
        self.val: FailT = val

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Invalid) and other.val == self.val

    def __repr__(self) -> str:
        return f"Invalid({repr(self.val)})"

    def apply(self, _: "Validated[Callable[[Any], B], FailT]") -> "Validated[B, FailT]":
        return self

    def get_or_else(self, fallback: A) -> A:
        return fallback

    def map(self, _: Callable[[Any], B]) -> "Validated[B, FailT]":
        return self

    def flat_map(
        self, _: Callable[[Any], "Validated[B, FailT]"]
    ) -> "Validated[B, FailT]":
        return self

    def flat_map_err(self, fn: Callable[[FailT], "Validated[A, B]"]) -> "Validated[A, B]":
        return fn(self.val)

    def map_err(self, fn: Callable[[FailT], B]) -> "Validated[A, B]":
        return Invalid(fn(self.val))

    @property
    def as_result(self) -> Result[Any, FailT]:
        return Ok(self.val)


Validated = Union[Valid[A], Invalid[FailT]]


class Validator(Generic[A, B, FailT]):
    """
    Essentially a `Callable[[A], Result[B, FailT]]`, but allows us to
    retain metadata from the validator (instead of hiding inside a closure). For
    instance, we can later access `5` from something like `MaxLength(5)`.
    """

    def __call__(self, val: A) -> Validated[B, FailT]:  # pragma: no cover
        raise NotImplementedError

    async def validate_async(self, val: A) -> Validated[B, FailT]:  # pragma: no cover
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
    def __call__(self, val: A) -> Validated[A, FailT]:
        if self.is_valid(val) is True:
            return Valid(val)
        else:
            return Invalid(self.err(val))


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
    async def validate_async(self, val: A) -> Validated[A, FailT]:
        if await self.is_valid_async(val) is True:
            return Valid(val)
        else:
            return Invalid(await self.err_async(val))


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
