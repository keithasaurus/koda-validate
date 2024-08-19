from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, ClassVar, Hashable, List, Optional, Set, Tuple, Type, TypeVar
from uuid import UUID

from koda import Thunk

from koda_validate._generics import A, Ret
from koda_validate._internal import _ResultTuple, _ToTupleValidator
from koda_validate.base import Predicate, Processor, Validator
from koda_validate.errors import PredicateErrs, TypeErr
from koda_validate.valid import Invalid, ValidationResult


class Lazy(Validator[Ret]):
    """
    Allows for specification of mutually recursive type definitions.
    """

    __match_args__ = (
        "validator",
        "recurrent",
    )

    def __init__(
        self,
        validator: Thunk[Validator[Ret]],
        recurrent: bool = True,
    ) -> None:
        """
        :param validator: the validator we actually want to use
        :param recurrent: whether this is being used in a recursive way. This
            is useful, so we can avoid infinite loops when traversing
            over validators (i.e. for openapi generation)
        """
        self.validator = validator
        self.recurrent = recurrent

    async def validate_async(self, data: Any) -> ValidationResult[Ret]:
        return await self.validator().validate_async(data)

    def __call__(self, data: Any) -> ValidationResult[Ret]:
        return self.validator()(data)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and self.validator == other.validator
            and self.recurrent == other.recurrent
        )

    def __repr__(self) -> str:
        return f"Lazy({repr(self.validator)}, recurrent={repr(self.recurrent)})"


ChoiceT = TypeVar("ChoiceT", bound=Hashable)


@dataclass
class Choices(Predicate[ChoiceT]):
    """
    A allow to check some ``Hashable`` type against a finite set of values.
    """

    choices: Set[ChoiceT]

    def __call__(self, val: ChoiceT) -> bool:
        return val in self.choices


MinMaxT = TypeVar("MinMaxT", int, float, Decimal, date, datetime)


@dataclass
class Min(Predicate[MinMaxT]):
    minimum: MinMaxT
    exclusive_minimum: bool = False

    def __call__(self, val: MinMaxT) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum


@dataclass
class Max(Predicate[MinMaxT]):
    maximum: MinMaxT
    exclusive_maximum: bool = False

    def __call__(self, val: MinMaxT) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum


Num = TypeVar("Num", int, float, Decimal)


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
    bytes,
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

    def __call__(self, val: ExactMatchT) -> bool:
        return val == self.match


@dataclass(init=False)
class EqualsValidator(_ToTupleValidator[ExactMatchT]):
    """
    Check if a value is of the same type as ``match`` *and* check that that
    value is equivalent.
    """

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

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[ExactMatchT]:
        return self._validate_to_tuple(val)

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[ExactMatchT]:
        if (match_type := type(self.match)) == type(val):
            if self.preprocessors:
                for preprocess in self.preprocessors:
                    val = preprocess(val)

            if self.predicate(val):
                return True, val
            else:
                return False, Invalid(PredicateErrs([self.predicate]), val, self)
        else:
            return False, Invalid(TypeErr(match_type), val, self)


class AlwaysValid(_ToTupleValidator[A]):
    """
    Whatever value is submitted for validation will be returned as valid
    """

    __match_args__ = ()

    _instance: ClassVar[Optional["AlwaysValid[Any]"]] = None

    def __new__(cls) -> "AlwaysValid[A]":
        # make a singleton
        if cls._instance is None:
            cls._instance = super(AlwaysValid, cls).__new__(cls)
        return cls._instance

    def _validate_to_tuple(self, val: A) -> _ResultTuple[A]:
        return True, val

    async def _validate_to_tuple_async(self, val: A) -> _ResultTuple[A]:
        return True, val

    def __repr__(self) -> str:
        return "AlwaysValid()"


# Any must be the generic param here, but, AlwaysValid() can take on any generic type
always_valid: AlwaysValid[Any] = AlwaysValid()

ListOrTupleOrSetAny = TypeVar("ListOrTupleOrSetAny", List[Any], Tuple[Any, ...], Set[Any])


@dataclass
class MinItems(Predicate[ListOrTupleOrSetAny]):
    item_count: int

    def __call__(self, val: ListOrTupleOrSetAny) -> bool:
        return len(val) >= self.item_count


@dataclass
class MaxItems(Predicate[ListOrTupleOrSetAny]):
    item_count: int

    def __call__(self, val: ListOrTupleOrSetAny) -> bool:
        return len(val) <= self.item_count


@dataclass
class ExactItemCount(Predicate[ListOrTupleOrSetAny]):
    item_count: int

    def __call__(self, val: ListOrTupleOrSetAny) -> bool:
        return len(val) == self.item_count


@dataclass
class UniqueItems(Predicate[ListOrTupleOrSetAny]):
    """
    Works with both hashable and unhashable items.
    """

    def __call__(self, val: ListOrTupleOrSetAny) -> bool:
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


# mypy has a problem with this for Tuple[Any, ...]
# for some types, you might need to use UniqueItems()
unique_items = UniqueItems()

StrOrBytes = TypeVar("StrOrBytes", str, bytes)


@dataclass
class MaxLength(Predicate[StrOrBytes]):
    length: int

    def __call__(self, val: StrOrBytes) -> bool:
        return len(val) <= self.length


@dataclass
class MinLength(Predicate[StrOrBytes]):
    length: int

    def __call__(self, val: StrOrBytes) -> bool:
        return len(val) >= self.length


@dataclass
class ExactLength(Predicate[StrOrBytes]):
    length: int

    def __call__(self, val: StrOrBytes) -> bool:
        return len(val) == self.length


@dataclass
class StartsWith(Predicate[StrOrBytes]):
    prefix: StrOrBytes

    def __call__(self, val: StrOrBytes) -> bool:
        return val.startswith(self.prefix)


@dataclass
class EndsWith(Predicate[StrOrBytes]):
    suffix: StrOrBytes

    def __call__(self, val: StrOrBytes) -> bool:
        return val.endswith(self.suffix)


@dataclass
class NotBlank(Predicate[StrOrBytes]):
    _instance: ClassVar[Optional["NotBlank[Any]"]] = None

    def __new__(cls) -> "NotBlank[StrOrBytes]":
        # make a singleton
        if cls._instance is None:
            cls._instance = super(NotBlank, cls).__new__(cls)
        return cls._instance

    def __call__(self, val: StrOrBytes) -> bool:
        return len(val.strip()) != 0


not_blank = NotBlank()


@dataclass
class Strip(Processor[StrOrBytes]):
    def __call__(self, val: StrOrBytes) -> StrOrBytes:
        return val.strip()


strip = Strip()


@dataclass
class UpperCase(Processor[StrOrBytes]):
    def __call__(self, val: StrOrBytes) -> StrOrBytes:
        return val.upper()


@dataclass
class LowerCase(Processor[StrOrBytes]):
    def __call__(self, val: StrOrBytes) -> StrOrBytes:
        return val.lower()


upper_case = UpperCase()

lower_case = LowerCase()
