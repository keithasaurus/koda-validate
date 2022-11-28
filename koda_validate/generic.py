from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional, Set, Tuple, Type, TypeVar
from uuid import UUID

from koda import Thunk
from koda._generics import A

from koda_validate._generics import Ret
from koda_validate.base import (
    InvalidType,
    Predicate,
    Processor,
    ValidationResult,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)
from koda_validate.validated import Invalid, Valid

EnumT = TypeVar("EnumT", str, int)


class Lazy(Validator[A, Ret]):
    __slots__ = (
        "validator",
        "recurrent",
    )
    __match_args__ = (
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

    async def validate_async(self, data: A) -> ValidationResult[Ret]:
        return await self.validator().validate_async(data)

    def __call__(self, data: A) -> ValidationResult[Ret]:
        return self.validator()(data)


@dataclass
class Choices(Predicate[EnumT]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    choices: Set[EnumT]

    def __call__(self, val: EnumT) -> bool:
        return val in self.choices


Num = TypeVar("Num", int, float, Decimal)


@dataclass
class Min(Predicate[Num]):
    minimum: Num
    exclusive_minimum: bool = False

    def __call__(self, val: Num) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum


@dataclass
class Max(Predicate[Num]):
    maximum: Num
    exclusive_maximum: bool = False

    def __call__(self, val: Num) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum


@dataclass
class MultipleOf(Predicate[Num]):
    factor: Num

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


@dataclass
class EqualTo(Predicate[ExactMatchT]):
    match: ExactMatchT

    def __call__(self, val: A) -> bool:
        return val == self.match


@dataclass(init=False)
class EqualsValidator(Validator[Any, ExactMatchT]):
    match: ExactMatchT
    preprocessors: Optional[List[Processor[ExactMatchT]]] = None

    def __init__(
        self,
        match: ExactMatchT,
        preprocessors: Optional[List[Processor[ExactMatchT]]] = None,
    ) -> None:
        self.match = match
        self.preprocessors = preprocessors
        self.predicate: EqualTo[ExactMatchT] = EqualTo(match)

    async def validate_async(self, val: Any) -> ValidationResult[ExactMatchT]:
        return self(val)

    def __call__(self, val: Any) -> ValidationResult[ExactMatchT]:
        if (match_type := type(self.match)) == type(val):
            if self.preprocessors:
                for preprocess in self.preprocessors:
                    val = preprocess(val)

            if self.predicate(val):
                return Valid(val)
            else:
                return Invalid([self.predicate])
        else:
            return Invalid(InvalidType(match_type, self))


class AlwaysValid(_ToTupleValidatorUnsafe[A, A]):
    __match_args__ = ()

    def validate_to_tuple(self, val: A) -> _ResultTupleUnsafe:
        return True, val

    async def validate_to_tuple_async(self, val: A) -> _ResultTupleUnsafe:
        return True, val


always_valid: _ToTupleValidatorUnsafe[Any, Any] = AlwaysValid()
ListOrTupleAny = TypeVar("ListOrTupleAny", List[Any], Tuple[Any, ...])


@dataclass
class MinItems(Predicate[ListOrTupleAny]):
    length: int

    def __call__(self, val: ListOrTupleAny) -> bool:
        return len(val) >= self.length


@dataclass
class MaxItems(Predicate[ListOrTupleAny]):
    length: int

    def __call__(self, val: ListOrTupleAny) -> bool:
        return len(val) <= self.length


@dataclass
class ExactItemCount(Predicate[ListOrTupleAny]):
    length: int

    def __call__(self, val: ListOrTupleAny) -> bool:
        return len(val) == self.length


@dataclass
class UniqueItems(Predicate[ListOrTupleAny]):
    def __call__(self, val: ListOrTupleAny) -> bool:
        hashable_items: Set[Tuple[Type[Any], Any]] = set()
        # slower lookups for unhashables
        unhashable_items: List[Tuple[Type[Any], Any]] = []
        for item in val:
            # needed to tell difference between things like
            # ints and bools
            typed_lookup = (type(item), item)
            try:
                if typed_lookup in hashable_items:
                    return False
                else:
                    hashable_items.add(typed_lookup)
            except TypeError:  # not hashable!
                if typed_lookup in unhashable_items:
                    return False
                else:
                    unhashable_items.append(typed_lookup)
        else:
            return True


unique_items = UniqueItems()
