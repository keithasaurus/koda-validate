from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional, Set, TypeVar
from uuid import UUID

from koda import Thunk
from koda._generics import A

from koda_validate._generics import Ret
from koda_validate.base import (
    Predicate,
    Processor,
    Serializable,
    ValidationErr,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)
from koda_validate.validated import Invalid, Valid, Validated

EnumT = TypeVar("EnumT", str, int)


class Lazy(Validator[A, Ret]):
    __match_args__ = (
        "validator",
        "recurrent",
    )
    __slots__ = (
        "validator",
        "recurrent",
    )

    def __init__(
        self,
        validator: Thunk[Validator[A, Ret]],
        recurrent: bool = True,
    ) -> None:
        """
        Args:
            validator: the validator we actually want to use
            recurrent: whether this is being used in a recursive way. This
                is useful, so we can avoid infinite loops when traversing
                over validators (i.e. for openapi generation)
        """
        self.validator = validator
        self.recurrent = recurrent

    def __call__(self, data: A) -> Validated[Ret, ValidationErr]:
        return self.validator()(data)

    async def validate_async(self, data: A) -> Validated[Ret, ValidationErr]:
        return await self.validator().validate_async(data)


@dataclass(init=False)
class Choices(Predicate[EnumT]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    def __init__(self, choices: Set[EnumT]) -> None:
        self.err_message = f"expected one of {sorted(choices)}"
        self.choices: Set[EnumT] = choices

    def __call__(self, val: EnumT) -> bool:
        return val in self.choices


Num = TypeVar("Num", int, float, Decimal)


@dataclass(init=False)
class Min(Predicate[Num]):
    minimum: Num
    exclusive_minimum: bool

    def __init__(self, minimum: Num, exclusive_minimum: bool = False) -> None:
        self.minimum: Num = minimum
        self.exclusive_minimum = exclusive_minimum
        exclusive = " (exclusive)" if self.exclusive_minimum else ""
        self.err_message = f"minimum allowed value{exclusive} is {self.minimum}"

    def __call__(self, val: Num) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum


@dataclass(init=False)
class Max(Predicate[Num]):
    maximum: Num
    exclusive_maximum: bool

    def __init__(self, maximum: Num, exclusive_maximum: bool = False) -> None:
        self.maximum: Num = maximum
        self.exclusive_maximum = exclusive_maximum
        exclusive = " (exclusive)" if self.exclusive_maximum else ""
        self.err_message = f"maximum allowed value{exclusive} is {self.maximum}"

    def __call__(self, val: Num) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum


@dataclass(init=False)
class MultipleOf(Predicate[Num]):
    def __init__(self, factor: Num) -> None:
        self.err_message = f"expected multiple of {factor}"
        self.factor: Num = factor

    def __call__(self, val: Num) -> bool:
        return val % self.factor == 0


# todo: expand types?
# note that we are allowing `float` because python allows float equivalence checks
# doesn't mean it's recommended to use it!
ExactMatchT = TypeVar(
    "ExactMatchT",
    bool,
    int,
    Decimal,
    str,
    float,
    date,
    datetime,
    UUID,
)


class EqualsValidator(Validator[Any, ExactMatchT]):
    __slots__ = ("match", "preprocessors")
    __match_args__ = ("match", "preprocessors")

    def __init__(
        self,
        match: ExactMatchT,
        preprocessors: Optional[List[Processor[ExactMatchT]]] = None,
    ) -> None:
        self.match: ExactMatchT = match
        self.preprocessors: Optional[List[Processor[ExactMatchT]]] = preprocessors

    def __call__(self, val: Any) -> Validated[ExactMatchT, ValidationErr]:
        if (match_type := type(self.match)) == type(val):
            if self.preprocessors:
                for preprocess in self.preprocessors:
                    val = preprocess(val)

            if self.match == val:
                return Valid(val)

        # ok, we've failed
        if isinstance(self.match, str):
            value_str = f'"{self.match}"'
        else:
            value_str = str(self.match)

        return Invalid([f"expected exactly {value_str} ({match_type.__name__})"])

    async def validate_async(self, val: Any) -> Validated[ExactMatchT, ValidationErr]:
        return self(val)


class AlwaysValid(_ToTupleValidatorUnsafe[A, A]):
    __match_args__ = ()

    def validate_to_tuple(self, val: A) -> _ResultTupleUnsafe:
        return True, val

    async def validate_to_tuple_async(self, val: A) -> _ResultTupleUnsafe:
        return True, val


always_valid: _ToTupleValidatorUnsafe[Any, Any] = AlwaysValid()
