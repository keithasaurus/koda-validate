from dataclasses import dataclass
from decimal import Decimal
from typing import Set, TypeVar

from koda import Result, Thunk
from koda._generics import A

from koda_validate._generics import Ret
from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import expected

EnumT = TypeVar("EnumT", str, int)


@dataclass(frozen=True, init=False)
class Lazy(Validator[A, Ret, JSONValue]):
    validator: Thunk[Validator[A, Ret, JSONValue]]
    recurrent: bool = True

    def __init__(
        self,
        validator: Thunk[Validator[A, Ret, JSONValue]],
        recurrent: bool = True,
    ) -> None:
        """
        Args:
            validator: the validator we actually want to use
            recurrent: whether this is being used in a recursive way. This
                is useful, so we can avoid infinite loops when traversing
                over validators (i.e. for openapi generation)
        """
        object.__setattr__(self, "validator", validator)
        object.__setattr__(self, "recurrent", recurrent)

    def __call__(self, data: A) -> Result[Ret, JSONValue]:
        return self.validator()(data)


@dataclass(frozen=True, init=False)
class Choices(Predicate[EnumT, JSONValue]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    choices: Set[EnumT]

    def __init__(self, choices: Set[EnumT]) -> None:
        object.__setattr__(self, "choices", choices)

    def is_valid(self, val: EnumT) -> bool:
        return val in self.choices

    def err_message(self, val: EnumT) -> JSONValue:
        return f"expected one of {sorted(self.choices)}"


Num = TypeVar("Num", int, float, Decimal)


@dataclass(frozen=True)
class Min(Predicate[Num, JSONValue]):
    minimum: Num
    exclusive_minimum: bool = False

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum

    def err_message(self, val: Num) -> str:
        return f"minimum allowed value is {self.minimum}"


@dataclass(frozen=True)
class Max(Predicate[Num, JSONValue]):
    maximum: Num
    exclusive_maximum: bool = False

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum

    def err_message(self, val: Num) -> str:
        return f"maximum allowed value is {self.maximum}"


@dataclass(frozen=True)
class MultipleOf(Predicate[Num, JSONValue]):
    factor: Num

    def is_valid(self, val: Num) -> bool:
        return val % self.factor == 0

    def err_message(self, val: Num) -> str:
        return f"expected multiple of {self.factor}"


# todo: consider expanding
ExactT = TypeVar("ExactT", str, int, Decimal)


@dataclass
class Exactly(Predicate[ExactT, JSONValue]):
    match: ExactT

    def is_valid(self, val: ExactT) -> bool:
        return val == self.match

    def err_message(self, val: ExactT) -> JSONValue:
        return expected(
            f'"{self.match}"' if isinstance(self.match, str) else str(self.match)
        )