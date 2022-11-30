from typing import Any, ClassVar, Generic, Literal, Union

from koda import Err, Ok, Result

from koda_validate._generics import A, FailT


class Valid(Generic[A]):
    __match_args__ = ("val",)

    is_valid: ClassVar[Literal[True]] = True

    def __init__(self, val: A) -> None:
        self.val: A = val

    @property
    def as_result(self) -> Result[A, Any]:
        return Ok(self.val)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Valid) and other.val == self.val

    def __repr__(self) -> str:
        return f"Valid({repr(self.val)})"


class Invalid(Generic[FailT]):
    __match_args__ = ("val",)

    is_valid: ClassVar[Literal[False]] = False

    def __init__(self, val: FailT) -> None:
        self.val: FailT = val

    @property
    def as_result(self) -> Result[Any, FailT]:
        return Err(self.val)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Invalid) and other.val == self.val

    def __repr__(self) -> str:
        return f"Invalid({repr(self.val)})"


Validated = Union[Valid[A], Invalid[FailT]]
