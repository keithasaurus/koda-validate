from typing import Any, Callable, ClassVar, Generic, Literal, Union

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
