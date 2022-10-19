import decimal
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal as DecimalStdLib
from json import loads
from typing import (
    Any,
    AnyStr,
    Callable,
    Final,
    Generic,
    Iterable,
    Optional,
    Pattern,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
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
from koda_validate.validators.validate_and_map import validate_and_map


def accum_errors_jsonish(
    val: A, validators: Iterable[Predicate[A, JSONValue]]
) -> Result[A, JSONValue]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return cast(Result[A, JSONValue], accum_errors(val, validators))


@dataclass(frozen=True)
class MaxLength(Predicate[str, JSONValue]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err_message(self, val: str) -> JSONValue:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinLength(Predicate[str, JSONValue]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err_message(self, val: str) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MinItems(Predicate[list[Any], JSONValue]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: list[Any]) -> bool:
        return len(val) >= self.length

    def err_message(self, val: list[Any]) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MaxItems(Predicate[list[Any], JSONValue]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: list[Any]) -> bool:
        return len(val) <= self.length

    def err_message(self, val: list[Any]) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinKeys(Predicate[dict[Any, Any], JSONValue]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err_message(self, val: dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxKeys(Predicate[dict[Any, Any], JSONValue]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err_message(self, val: dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


class UniqueItems(Predicate[list[Any], JSONValue]):
    def is_valid(self, val: list[Any]) -> bool:
        hashable_items: Set[Tuple[Type[Any], Any]] = set()
        # slower lookups for unhashables
        unhashable_items: list[Tuple[Type[Any], Any]] = []
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

    def err_message(self, val: list[Any]) -> str:
        return "all items must be unique"


unique_items = UniqueItems()


class BooleanValidator(Validator[Any, bool, JSONValue]):
    def __init__(self, *validators: Predicate[bool, JSONValue]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[bool, JSONValue]:
        if isinstance(val, bool):
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("a boolean")])


class StringValidator(Validator[Any, str, JSONValue]):
    def __init__(self, *validators: Predicate[str, JSONValue]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[str, JSONValue]:
        if isinstance(val, str):
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("a string")])


@dataclass(frozen=True)
class RegexValidator(Predicate[str, JSONValue]):
    pattern: Pattern[str]

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message(self, val: str) -> str:
        return rf"must match pattern {self.pattern.pattern}"


@dataclass(frozen=True)
class Email(Predicate[str, JSONValue]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message(self, val: str) -> str:
        return "expected a valid email address"


class IntValidator(Validator[Any, int, JSONValue]):
    def __init__(self, *validators: Predicate[int, JSONValue]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[int, JSONValue]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("an integer")])


class FloatValidator(Validator[Any, float, JSONValue]):
    def __init__(self, *validators: Predicate[float, JSONValue]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("a float")])


class DecimalValidator(Validator[Any, DecimalStdLib, JSONValue]):
    def __init__(self, *validators: Predicate[DecimalStdLib, JSONValue]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[DecimalStdLib, JSONValue]:
        expected_msg = expected("a decimal-compatible string or integer")
        if isinstance(val, DecimalStdLib):
            return Ok(val)
        elif isinstance(val, (str, int)):
            try:
                return Ok(DecimalStdLib(val))
            except decimal.InvalidOperation:
                return Err([expected_msg])
        else:
            return Err([expected_msg])


def _safe_try_int(val: Any) -> Result[int, Exception]:
    return safe_try(int, val)


class DateValidator(Validator[Any, date, JSONValue]):
    """
    Expects dates to be yyyy-mm-dd
    """

    def __init__(self, *validators: Predicate[date, JSONValue]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[date, JSONValue]:
        fail_msg: Result[date, JSONValue] = Err(["expected date formatted as yyyy-mm-dd"])
        if isinstance(val, str):
            try:
                year, month, day = val.split("-")
            except Exception:
                return fail_msg
            else:
                if len(year) != 4 or len(month) != 2 or len(day) != 2:
                    return fail_msg
                result = validate_and_map(
                    date, _safe_try_int(year), _safe_try_int(month), _safe_try_int(day)
                )
                if isinstance(result, Err):
                    return fail_msg
                else:
                    return accum_errors_jsonish(result.val, self.validators)
        else:
            return fail_msg


class ListValidator(Validator[Any, list[A], JSONValue]):
    def __init__(
        self,
        item_validator: Validator[Any, A, JSONValue],
        *list_validators: Predicate[list[Any], JSONValue],
    ) -> None:
        self.item_validator = item_validator
        self.list_validators = list_validators

    def __call__(self, val: Any) -> Result[list[A], JSONValue]:
        if isinstance(val, list):
            return_list: list[A] = []
            errors: dict[str, JSONValue] = {}

            list_errors: list[JSONValue] = []
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
                    errors[f"index {i}"] = item_result.val

            if len(errors) > 0:
                return Err(errors)
            else:
                return Ok(return_list)
        else:
            return Err({"invalid type": [expected("an array")]})


EnumT = TypeVar("EnumT", str, int)


class Lazy(Validator[A, Ret, JSONValue]):
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
        self.validator = validator
        self.recurrent = recurrent

    def __call__(self, data: A) -> Result[Ret, JSONValue]:
        return self.validator()(data)


class Choices(Predicate[EnumT, JSONValue]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    def __init__(self, choices: Set[EnumT]) -> None:
        self.choices: Set[EnumT] = choices

    def is_valid(self, val: EnumT) -> bool:
        return val in self.choices

    def err_message(self, val: EnumT) -> JSONValue:
        return f"expected one of {sorted(self.choices)}"


KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, JSONValue]]]


def _validate_with_key(
    r: KeyValidator[A], data: dict[Any, Any]
) -> Result[A, Tuple[str, JSONValue]]:
    key, fn = r

    def add_key(val: JSONValue) -> Tuple[str, JSONValue]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)


class OneOf2(Validator[Any, Either[A, B], JSONValue]):
    def __init__(
        self,
        variant_one: Union[
            Validator[Any, A, JSONValue],
            Tuple[str, Validator[Any, A, JSONValue]],
        ],
        variant_two: Union[
            Validator[Any, B, JSONValue],
            Tuple[str, Validator[Any, B, JSONValue]],
        ],
    ) -> None:
        if isinstance(variant_one, tuple):
            self.variant_one_label, self.variant_one = variant_one
        else:
            self.variant_one = variant_one
            self.variant_one_label = "variant 1"

        if isinstance(variant_two, tuple):
            self.variant_two_label, self.variant_two = variant_two
        else:
            self.variant_two = variant_two
            self.variant_two_label = "variant 2"

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
                        self.variant_one_label: v1_result.val,
                        self.variant_two_label: v2_result.val,
                    }
                )


class OneOf3(Validator[Any, Either3[A, B, C], JSONValue]):
    def __init__(
        self,
        variant_one: Union[
            Validator[Any, A, JSONValue],
            Tuple[str, Validator[Any, A, JSONValue]],
        ],
        variant_two: Union[
            Validator[Any, B, JSONValue],
            Tuple[str, Validator[Any, B, JSONValue]],
        ],
        variant_three: Union[
            Validator[Any, C, JSONValue],
            Tuple[str, Validator[Any, C, JSONValue]],
        ],
    ) -> None:
        if isinstance(variant_one, tuple):
            self.variant_one_label, self.variant_one = variant_one
        else:
            self.variant_one = variant_one
            self.variant_one_label = "variant 1"

        if isinstance(variant_two, tuple):
            self.variant_two_label, self.variant_two = variant_two
        else:
            self.variant_two = variant_two
            self.variant_two_label = "variant 2"

        if isinstance(variant_three, tuple):
            self.variant_three_label, self.variant_three = variant_three
        else:
            self.variant_three = variant_three
            self.variant_three_label = "variant 3"

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
                            self.variant_one_label: v1_result.val,
                            self.variant_two_label: v2_result.val,
                            self.variant_three_label: v3_result.val,
                        }
                    )


BLANK_STRING_MSG: Final[str] = "cannot be blank"


class NotBlank(Predicate[str, JSONValue]):
    def is_valid(self, val: str) -> bool:
        return len(val.strip()) != 0

    def err_message(self, val: str) -> JSONValue:
        return BLANK_STRING_MSG


not_blank = NotBlank()

_KEY_MISSING: Final[str] = "key missing"


class RequiredField(Generic[A]):
    def __init__(self, validator: Validator[Any, A, JSONValue]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, JSONValue]:
        if isinstance(maybe_val, Nothing):
            return Err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


class MaybeField(Generic[A]):
    def __init__(self, validator: Validator[Any, A, JSONValue]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], JSONValue]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], JSONValue] = self.validator(maybe_val.val).map(Just)
        else:
            result = Ok(maybe_val)
        return result


def deserialize_and_validate(
    validator: Validator[Any, A, JSONValue], data: AnyStr
) -> Result[A, JSONValue]:
    try:
        deserialized = loads(data)
    except Exception:
        return Err({"bad data": "invalid json"})
    else:
        return validator(deserialized)


def _variant_errors(*variants: JSONValue) -> JSONValue:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


class Nullable(Validator[Any, Maybe[A], JSONValue]):
    """
    We have a value for a key, but it can be null (None)
    """

    def __init__(self, validator: Validator[Any, A, JSONValue]) -> None:
        self.validator = validator

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


Num = TypeVar("Num", int, float, DecimalStdLib)


@dataclass(frozen=True)
class Minimum(Predicate[Num, JSONValue]):
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
class Maximum(Predicate[Num, JSONValue]):
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
