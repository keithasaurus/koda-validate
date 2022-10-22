import decimal
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal as Decimal
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from koda import mapping_get, safe_try
from koda._generics import A
from koda.either import Either, Either3, First, Second, Third
from koda.maybe import Just, Maybe, Nothing, nothing
from koda.result import Err, Ok, Result

from koda_validate._generics import B, C, Ret
from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import accum_errors, expected


def accum_errors_json(
    val: A, validators: Iterable[Predicate[A, JSONValue]]
) -> Result[A, JSONValue]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return cast(Result[A, JSONValue], accum_errors(val, validators))


@dataclass(frozen=True)
class MaxLength(Predicate[str, JSONValue]):
    length: int

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err_message(self, val: str) -> JSONValue:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinLength(Predicate[str, JSONValue]):
    length: int

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err_message(self, val: str) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MinItems(Predicate[List[Any], JSONValue]):
    length: int

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) >= self.length

    def err_message(self, val: List[Any]) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MaxItems(Predicate[List[Any], JSONValue]):
    length: int

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) <= self.length

    def err_message(self, val: List[Any]) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinKeys(Predicate[Dict[Any, Any], JSONValue]):
    size: int

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err_message(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxKeys(Predicate[Dict[Any, Any], JSONValue]):
    size: int

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err_message(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


class UniqueItems(Predicate[List[Any], JSONValue]):
    def is_valid(self, val: List[Any]) -> bool:
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

    def err_message(self, val: List[Any]) -> str:
        return "all items must be unique"


unique_items = UniqueItems()


@dataclass(init=False, frozen=True)
class BooleanValidator(Validator[Any, bool, JSONValue]):
    predicates: Tuple[Predicate[bool, JSONValue], ...]

    def __init__(self, *predicates: Predicate[bool, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[bool, JSONValue]:
        if isinstance(val, bool):
            return accum_errors_json(val, self.predicates)
        else:
            return Err([expected("a boolean")])


@dataclass(init=False, frozen=True)
class IntValidator(Validator[Any, int, JSONValue]):
    predicates: Tuple[Predicate[int, JSONValue]]

    def __init__(self, *predicates: Predicate[int, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[int, JSONValue]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors_json(val, self.predicates)
        else:
            return Err([expected("an integer")])


@dataclass(init=False, frozen=True)
class FloatValidator(Validator[Any, float, JSONValue]):
    predicates: Tuple[Predicate[float, JSONValue], ...]

    def __init__(self, *predicates: Predicate[float, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return accum_errors_json(val, self.predicates)
        else:
            return Err([expected("a float")])


@dataclass(init=False, frozen=True)
class DecimalValidator(Validator[Any, Decimal, JSONValue]):
    predicates: Tuple[Predicate[Decimal, JSONValue], ...]

    def __init__(self, *predicates: Predicate[Decimal, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[Decimal, JSONValue]:
        expected_msg = expected("a decimal-compatible string or integer")
        if isinstance(val, Decimal):
            return Ok(val)
        elif isinstance(val, (str, int)):
            try:
                return Ok(Decimal(val))
            except decimal.InvalidOperation:
                return Err([expected_msg])
        else:
            return Err([expected_msg])


def _safe_try_int(val: Any) -> Result[int, Exception]:
    return safe_try(int, val)


@dataclass(frozen=True, init=False)
class DateValidator(Validator[Any, date, JSONValue]):
    """
    Expects dates to be yyyy-mm-dd
    """

    predicates: Tuple[Predicate[date, JSONValue], ...]

    def __init__(self, *predicates: Predicate[date, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[date, JSONValue]:
        try:
            return Ok(date.fromisoformat(val))
        except (ValueError, TypeError):
            return Err(["expected date formatted as yyyy-mm-dd"])


@dataclass(frozen=True, init=False)
class DatetimeValidator(Validator[Any, date, JSONValue]):
    predicates: Tuple[Predicate[date, JSONValue], ...]

    def __init__(self, *predicates: Predicate[date, JSONValue]) -> None:
        object.__setattr__(self, "predicates", predicates)

    def __call__(self, val: Any) -> Result[date, JSONValue]:
        try:
            # note isoparse from dateutil is more flexible if we want
            # to add the dependency at some point
            return Ok(datetime.fromisoformat(val))
        except (ValueError, TypeError):
            return Err([expected("iso8601-formatted string")])


@dataclass(frozen=True, init=False)
class ListValidator(Validator[Any, List[A], JSONValue]):
    item_validator: Validator[Any, A, JSONValue]
    list_validators: Tuple[Predicate[List[A], JSONValue], ...]

    def __init__(
        self,
        item_validator: Validator[Any, A, JSONValue],
        *list_validators: Predicate[List[A], JSONValue],
    ) -> None:
        object.__setattr__(self, "item_validator", item_validator)
        object.__setattr__(self, "list_validators", list_validators)

    def __call__(self, val: Any) -> Result[List[A], JSONValue]:
        if isinstance(val, list):
            return_list: List[A] = []
            errors: Dict[str, JSONValue] = {}

            list_errors: List[JSONValue] = []
            for validator in self.list_validators:
                result = validator(val)

                if isinstance(result, Err):
                    list_errors.append(result.val)

            if len(list_errors) > 0:
                errors["__container__"] = list_errors

            for i, item in enumerate(val):
                item_result = self.item_validator(item)
                if isinstance(item_result, Ok):
                    return_list.append(item_result.val)
                else:
                    errors[str(i)] = item_result.val

            if len(errors) > 0:
                return Err(errors)
            else:
                return Ok(return_list)
        else:
            return Err({"__container__": [expected("a list")]})


EnumT = TypeVar("EnumT", str, int)


@dataclass(frozen=True, init=False)
class Lazy(Validator[A, Ret, JSONValue]):
    validator: Callable[[], Validator[A, Ret, JSONValue]]
    recurrent: bool = True

    def __init__(
        self,
        validator: Callable[[], Validator[A, Ret, JSONValue]],
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


KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, JSONValue]]]


def _validate_with_key(
    r: KeyValidator[A], data: Dict[Any, Any]
) -> Result[A, Tuple[str, JSONValue]]:
    key, fn = r

    def add_key(val: JSONValue) -> Tuple[str, JSONValue]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)


@dataclass(frozen=True, init=False)
class OneOf2(Validator[Any, Either[A, B], JSONValue]):
    variant_one: Validator[Any, A, JSONValue]
    variant_two: Validator[Any, B, JSONValue]

    def __init__(
        self,
        variant_one: Validator[Any, A, JSONValue],
        variant_two: Validator[Any, B, JSONValue],
    ) -> None:
        object.__setattr__(self, "variant_one", variant_one)
        object.__setattr__(self, "variant_two", variant_two)

    def __call__(self, val: Any) -> Result[Either[A, B], JSONValue]:
        v1_result = self.variant_one(val)

        if isinstance(v1_result, Ok):
            return Ok(First(v1_result.val))
        else:
            v2_result = self.variant_two(val)

            if isinstance(v2_result, Ok):
                return Ok(Second(v2_result.val))
            else:
                return Err(
                    {
                        "variant 1": v1_result.val,
                        "variant 2": v2_result.val,
                    }
                )


@dataclass(init=False, frozen=True)
class OneOf3(Validator[Any, Either3[A, B, C], JSONValue]):
    variant_one: Validator[Any, A, JSONValue]
    variant_two: Validator[Any, B, JSONValue]
    variant_three: Validator[Any, C, JSONValue]

    def __init__(
        self,
        variant_one: Validator[Any, A, JSONValue],
        variant_two: Validator[Any, B, JSONValue],
        variant_three: Validator[Any, C, JSONValue],
    ) -> None:
        object.__setattr__(self, "variant_one", variant_one)
        object.__setattr__(self, "variant_two", variant_two)
        object.__setattr__(self, "variant_three", variant_three)

    def __call__(self, val: Any) -> Result[Either3[A, B, C], JSONValue]:
        v1_result = self.variant_one(val)

        if isinstance(v1_result, Ok):
            return Ok(First(v1_result.val))
        else:
            v2_result = self.variant_two(val)

            if isinstance(v2_result, Ok):
                return Ok(Second(v2_result.val))
            else:
                v3_result = self.variant_three(val)

                if isinstance(v3_result, Ok):
                    return Ok(Third(v3_result.val))
                else:
                    return Err(
                        {
                            "variant 1": v1_result.val,
                            "variant 2": v2_result.val,
                            "variant 3": v3_result.val,
                        }
                    )


_KEY_MISSING: Final[str] = "key missing"


@dataclass(frozen=True)
class RequiredField(Generic[A]):
    validator: Validator[Any, A, JSONValue]

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, JSONValue]:
        if isinstance(maybe_val, Nothing):
            return Err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


@dataclass(frozen=True)
class MaybeField(Generic[A]):
    validator: Validator[Any, A, JSONValue]

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], JSONValue]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], JSONValue] = self.validator(maybe_val.val).map(Just)
        else:
            result = Ok(maybe_val)
        return result


def _variant_errors(*variants: JSONValue) -> JSONValue:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


@dataclass(frozen=True)
class Noneable(Validator[Any, Maybe[A], JSONValue]):
    """
    We have a value for a key, but it can be null (None)
    """

    validator: Validator[Any, A, JSONValue]

    def __call__(self, val: Optional[Any]) -> Result[Maybe[A], JSONValue]:
        if val is None:
            return Ok(nothing)
        else:
            result: Result[A, JSONValue] = self.validator(val)
            if isinstance(result, Ok):
                return result.map(Just)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )


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


class NoneValidator(Validator[Any, None, JSONValue]):
    def __call__(self, val: Any) -> Result[None, JSONValue]:
        if val is None:
            return Ok(val)
        else:
            return Err([expected("null")])


none_validator = NoneValidator()


def key(
    prop_: str, validator: Validator[Any, A, JSONValue]
) -> Tuple[str, Callable[[Any], Result[A, JSONValue]]]:
    return prop_, RequiredField(validator)


def maybe_key(
    prop_: str, validator: Validator[Any, A, JSONValue]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], JSONValue]]]:
    return prop_, MaybeField(validator)


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
