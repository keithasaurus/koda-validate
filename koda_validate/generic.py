from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional, Set, TypeVar
from uuid import UUID

from koda import Err, Ok, Result, Thunk
from koda._generics import A

from koda_validate._generics import Ret
from koda_validate.typedefs import Predicate, Processor, Serializable, Validator
from koda_validate.utils import expected

EnumT = TypeVar("EnumT", str, int)


@dataclass(frozen=True, init=False)
class Lazy(Validator[A, Ret, Serializable]):
    validator: Thunk[Validator[A, Ret, Serializable]]
    recurrent: bool = True

    def __init__(
        self,
        validator: Thunk[Validator[A, Ret, Serializable]],
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

    def __call__(self, data: A) -> Result[Ret, Serializable]:
        return self.validator()(data)


@dataclass(frozen=True, init=False)
class Choices(Predicate[EnumT, Serializable]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    choices: Set[EnumT]

    def __init__(self, choices: Set[EnumT]) -> None:
        object.__setattr__(self, "choices", choices)

    def is_valid(self, val: EnumT) -> bool:
        return val in self.choices

    def err(self, val: EnumT) -> Serializable:
        return f"expected one of {sorted(self.choices)}"


Num = TypeVar("Num", int, float, Decimal)


@dataclass(frozen=True)
class Min(Predicate[Num, Serializable]):
    minimum: Num
    exclusive_minimum: bool = False

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum

    def err(self, val: Num) -> str:
        exclusive = " (exclusive)" if self.exclusive_minimum else ""
        return f"minimum allowed value{exclusive} is {self.minimum}"


@dataclass(frozen=True)
class Max(Predicate[Num, Serializable]):
    maximum: Num
    exclusive_maximum: bool = False

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum

    def err(self, val: Num) -> str:
        exclusive = " (exclusive)" if self.exclusive_maximum else ""
        return f"maximum allowed value{exclusive} is {self.maximum}"


@dataclass(frozen=True)
class MultipleOf(Predicate[Num, Serializable]):
    factor: Num

    def is_valid(self, val: Num) -> bool:
        return val % self.factor == 0

    def err(self, val: Num) -> str:
        return f"expected multiple of {self.factor}"


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


@dataclass(frozen=True)
class ExactValidator(Validator[Any, ExactMatchT, Serializable]):
    match: ExactMatchT
    preprocessors: Optional[List[Processor[ExactMatchT]]] = None

    def __call__(self, val: Any) -> Result[ExactMatchT, Serializable]:
        if (match_type := type(self.match)) == type(val):
            if self.preprocessors is not None:
                for preprocess in self.preprocessors:
                    val = preprocess(val)

            if self.match == val:
                return Ok(val)

        # ok, we've failed
        if isinstance(self.match, str):
            value_str = f'"{self.match}"'
        else:
            value_str = str(self.match)

        return Err([expected(f"exactly {value_str} ({match_type.__name__})")])
