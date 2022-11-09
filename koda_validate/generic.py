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
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)
from koda_validate.validated import Invalid, Valid, Validated

EnumT = TypeVar("EnumT", str, int)


class Lazy(Validator[A, Ret, Serializable]):
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
        self.validator = validator
        self.recurrent = recurrent

    def __call__(self, data: A) -> Validated[Ret, Serializable]:
        return self.validator()(data)

    async def validate_async(self, data: A) -> Validated[Ret, Serializable]:
        return await self.validator().validate_async(data)


class Choices(Predicate[EnumT, Serializable]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    __slots__ = ("choices", "_err")
    __match_args__ = ("choices",)

    def __init__(self, choices: Set[EnumT]) -> None:
        self.choices: Set[EnumT] = choices
        self._err = f"expected one of {sorted(self.choices)}"

    def is_valid(self, val: EnumT) -> bool:
        return val in self.choices

    def err(self, val: EnumT) -> Serializable:
        return self._err


Num = TypeVar("Num", int, float, Decimal)


class Min(Predicate[Num, Serializable]):
    __slots__ = (
        "minimum",
        "exclusive_minimum",
        "_err",
    )
    __match_args__ = ("minimum", "exclusive_minimum")

    def __init__(self, minimum: Num, exclusive_minimum: bool = False) -> None:
        self.minimum: Num = minimum
        self.exclusive_minimum = exclusive_minimum
        exclusive = " (exclusive)" if self.exclusive_minimum else ""
        self._err = f"minimum allowed value{exclusive} is {self.minimum}"

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum

    def err(self, val: Num) -> str:
        return self._err


class Max(Predicate[Num, Serializable]):
    __slots__ = ("maximum", "exclusive_maximum", "_err")
    __match_args__ = ("maximum", "exclusive_maximum")

    def __init__(self, maximum: Num, exclusive_maximum: bool = False) -> None:
        self.maximum: Num = maximum
        self.exclusive_maximum = exclusive_maximum
        exclusive = " (exclusive)" if self.exclusive_maximum else ""
        self._err = f"maximum allowed value{exclusive} is {self.maximum}"

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum

    def err(self, val: Num) -> str:
        return self._err


class MultipleOf(Predicate[Num, Serializable]):
    __slots__ = ("factor",)
    __match_args__ = ("factor",)

    def __init__(self, factor: Num) -> None:
        self.factor: Num = factor

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


class ExactValidator(Validator[Any, ExactMatchT, Serializable]):
    __slots__ = ("match", "preprocessors")
    __match_args__ = ("match", "preprocessors")

    def __init__(
        self,
        match: ExactMatchT,
        preprocessors: Optional[List[Processor[ExactMatchT]]] = None,
    ) -> None:
        self.match: ExactMatchT = match
        self.preprocessors: Optional[List[Processor[ExactMatchT]]] = preprocessors

    def __call__(self, val: Any) -> Validated[ExactMatchT, Serializable]:
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

    async def validate_async(self, val: Any) -> Validated[ExactMatchT, Serializable]:
        return self(val)


class AlwaysValid(_ToTupleValidatorUnsafe[A, A, Serializable]):
    __match_args__ = ()

    def validate_to_tuple(self, val: A) -> _ResultTupleUnsafe:
        return True, val

    async def validate_to_tuple_async(self, val: A) -> _ResultTupleUnsafe:
        return True, val


always_valid: _ToTupleValidatorUnsafe[Any, Any, Serializable] = AlwaysValid()
