from __future__ import annotations  # for | Union type syntax

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

from koda_validate._cruft import _flat_map_same_type_if_not_none, _typed_tuple
from koda_validate._generics import B, C, D, E, F, G, H, I, J, Ret
from koda_validate.typedefs import (
    JSONValue,
    Predicate,
    PredicateJson,
    Validator,
    ValidatorFunc,
)
from koda_validate.utils import accum_errors, expected, validate_and_map

OBJECT_ERRORS_FIELD: Final[str] = "__object__"


def accum_errors_jsonish(
    val: A, validators: Iterable[Predicate[A, JSONValue]]
) -> Result[A, JSONValue]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return cast(Result[A, JSONValue], accum_errors(val, validators))


@dataclass(frozen=True)
class MaxLength(PredicateJson[str]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err_message_str(self, val: str) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinLength(PredicateJson[str]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err_message_str(self, val: str) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MinItems(PredicateJson[list[Any]]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: list[Any]) -> bool:
        return len(val) >= self.length

    def err_message_str(self, val: list[Any]) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MaxItems(PredicateJson[list[Any]]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: list[Any]) -> bool:
        return len(val) <= self.length

    def err_message_str(self, val: list[Any]) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinKeys(PredicateJson[dict[Any, Any]]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err_message_str(self, val: dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxKeys(PredicateJson[dict[Any, Any]]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err_message_str(self, val: dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


class UniqueItems(PredicateJson[list[Any]]):
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

    def err_message_str(self, val: list[Any]) -> str:
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
class RegexValidator(PredicateJson[str]):
    pattern: Pattern[str]

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message_str(self, val: str) -> str:
        return rf"must match pattern {self.pattern.pattern}"


@dataclass(frozen=True)
class Email(PredicateJson[str]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message_str(self, val: str) -> str:
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
                    _safe_try_int(year), _safe_try_int(month), _safe_try_int(day), date
                )
                if isinstance(result, Err):
                    return fail_msg
                else:
                    return accum_errors_jsonish(result.val, self.validators)
        else:
            return fail_msg


class MapValidator(Validator[Any, dict[A, B], JSONValue]):
    """
    Note that while a key should always be expected to be received as a string,
    it's possible that we may want to validate and cast it to a different
    type (i.e. a date)
    """

    def __init__(
        self,
        key_validator: Validator[Any, A, JSONValue],
        value_validator: Validator[Any, B, JSONValue],
        *dict_validators: Predicate[dict[A, B], JSONValue],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.dict_validators = dict_validators

    def __call__(self, data: Any) -> Result[dict[A, B], JSONValue]:
        if isinstance(data, dict):
            return_dict: dict[A, B] = {}
            errors: dict[str, JSONValue] = {}
            for key, val in data.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val)

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    if isinstance(key_result, Err):
                        errors[f"{key} (key)"] = key_result.val

                    if isinstance(val_result, Err):
                        errors[key] = val_result.val

            dict_validator_errors: list[JSONValue] = []
            for validator in self.dict_validators:
                # Note that the expectation here is that validators will likely
                # be doing json like number of keys; they aren't expected
                # to be drilling down into specific keys and values. That may be
                # an incorrect assumption; if so, some minor refactoring is probably
                # necessary.
                result = validator(data)
                if isinstance(result, Err):
                    dict_validator_errors.append(result.val)

            if len(dict_validator_errors) > 0:
                # in case somehow there are already errors in this field
                if OBJECT_ERRORS_FIELD in errors:
                    dict_validator_errors.append(errors[OBJECT_ERRORS_FIELD])

                errors[OBJECT_ERRORS_FIELD] = dict_validator_errors

            if errors:
                return Err(errors)
            else:
                return Ok(return_dict)
        else:
            return Err({"invalid type": [expected("a map")]})


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
                errors["__array__"] = list_errors

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


class Choices(PredicateJson[EnumT]):
    """
    This only exists separately from a more generic form because
    mypy was having difficulty understanding the narrowed generic types. mypy 0.800
    """

    def __init__(self, choices: Set[EnumT]) -> None:
        self.choices: Set[EnumT] = choices

    def is_valid(self, val: EnumT) -> bool:
        return val in self.choices

    def err_message_str(self, val: EnumT) -> str:
        return f"expected one of {sorted(self.choices)}"


KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, JSONValue]]]


def _validate_with_key(
    r: KeyValidator[A], data: dict[Any, Any]
) -> Result[A, Tuple[str, JSONValue]]:
    key, fn = r

    def add_key(val: JSONValue) -> Tuple[str, JSONValue]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)


class IsDict(Validator[Any, dict[Any, Any], JSONValue]):
    def __call__(self, val: Any) -> Result[dict[Any, Any], JSONValue]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return Err({OBJECT_ERRORS_FIELD: [expected("an object")]})


def _dict_without_extra_keys(
    keys: Set[str], data: Any
) -> Result[dict[Any, Any], JSONValue]:
    return IsDict()(data).flat_map(_has_no_extra_keys(keys))


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


def _tuple_to_dict_errors(errs: Tuple[JSONValue, ...]) -> dict[str, JSONValue]:
    return {f"index {i}": err for i, err in enumerate(errs)}


class Tuple2Validator(Validator[Any, Tuple[A, B], JSONValue]):
    required_length: int = 2

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, JSONValue]],
        slot2_validator: Callable[[Any], Result[B, JSONValue]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B]], Result[Tuple[A, B], JSONValue]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B], JSONValue]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B], Tuple[JSONValue, ...]] = validate_and_map(
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
                _typed_tuple,
            )

            if isinstance(result, Err):
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return Err(
                {"invalid type": [f"expected array of length {self.required_length}"]}
            )


class Tuple3Validator(Validator[Any, Tuple[A, B, C], JSONValue]):
    required_length: int = 3

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, JSONValue]],
        slot2_validator: Callable[[Any], Result[B, JSONValue]],
        slot3_validator: Callable[[Any], Result[C, JSONValue]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B, C]], Result[Tuple[A, B, C], JSONValue]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B, C], JSONValue]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B, C], Tuple[JSONValue, ...]] = validate_and_map(
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
                self.slot3_validator(data[2]),
                _typed_tuple,
            )

            if isinstance(result, Err):
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return Err(
                {"invalid type": [f"expected array of length {self.required_length}"]}
            )


def _has_no_extra_keys(
    keys: Set[str],
) -> ValidatorFunc[dict[A, B], dict[A, B], JSONValue]:
    def inner(mapping: dict[A, B]) -> Result[dict[A, B], JSONValue]:
        if len(mapping.keys() - keys) > 0:
            return Err(
                {
                    OBJECT_ERRORS_FIELD: [
                        f"Received unknown keys. Only expected {sorted(keys)}"
                    ]
                }
            )
        else:
            return Ok(mapping)

    return inner


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


class Noneable(Validator[Any, Maybe[A], JSONValue]):
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
class Minimum(PredicateJson[Num]):
    minimum: Num
    exclusive_minimum: bool = False

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_minimum:
            return val > self.minimum
        else:
            return val >= self.minimum

    def err_message_str(self, val: Num) -> str:
        return f"minimum allowed value is {self.minimum}"


@dataclass(frozen=True)
class Maximum(PredicateJson[Num]):
    maximum: Num
    exclusive_maximum: bool = False

    def is_valid(self, val: Num) -> bool:
        if self.exclusive_maximum:
            return val < self.maximum
        else:
            return val <= self.maximum

    def err_message_str(self, val: Num) -> str:
        return f"maximum allowed value is {self.maximum}"


@dataclass(frozen=True)
class MultipleOf(PredicateJson[Num]):
    factor: Num

    def is_valid(self, val: Num) -> bool:
        return val % self.factor == 0

    def err_message_str(self, val: Num) -> str:
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


def _tuples_to_jo_dict(data: Tuple[Tuple[str, JSONValue], ...]) -> JSONValue:
    return dict(data)


class Dict1KeyValidator(Generic[A, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        field1: KeyValidator[A],
        *,
        into: Callable[[A], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (field1,)
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val), self.into
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict2KeysValidator(Generic[A, B, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        *,
        into: Callable[[A, B], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict3KeysValidator(Generic[A, B, C, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        *,
        into: Callable[[A, B, C], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict4KeysValidator(Generic[A, B, C, D, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        *,
        into: Callable[[A, B, C, D], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict5KeysValidator(Generic[A, B, C, D, E, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        *,
        into: Callable[[A, B, C, D, E], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                _validate_with_key(self.fields[4], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict6KeysValidator(Generic[A, B, C, D, E, F, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        field6: KeyValidator[F],
        *,
        into: Callable[[A, B, C, D, E, F], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                _validate_with_key(self.fields[4], result.val),
                _validate_with_key(self.fields[5], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict7KeysValidator(
    Generic[A, B, C, D, E, F, G, Ret], Validator[Any, Ret, JSONValue]
):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        field6: KeyValidator[F],
        field7: KeyValidator[G],
        *,
        into: Callable[[A, B, C, D, E, F, G], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                _validate_with_key(self.fields[4], result.val),
                _validate_with_key(self.fields[5], result.val),
                _validate_with_key(self.fields[6], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict8KeysValidator(
    Generic[A, B, C, D, E, F, G, H, Ret], Validator[Any, Ret, JSONValue]
):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        field6: KeyValidator[F],
        field7: KeyValidator[G],
        field8: KeyValidator[H],
        *,
        into: Callable[[A, B, C, D, E, F, G, H], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            field8,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                _validate_with_key(self.fields[4], result.val),
                _validate_with_key(self.fields[5], result.val),
                _validate_with_key(self.fields[6], result.val),
                _validate_with_key(self.fields[7], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict9KeysValidator(
    Generic[A, B, C, D, E, F, G, H, I, Ret], Validator[Any, Ret, JSONValue]
):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        field6: KeyValidator[F],
        field7: KeyValidator[G],
        field8: KeyValidator[H],
        field9: KeyValidator[I],
        *,
        into: Callable[[A, B, C, D, E, F, G, H, I], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            field8,
            field9,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                _validate_with_key(self.fields[4], result.val),
                _validate_with_key(self.fields[5], result.val),
                _validate_with_key(self.fields[6], result.val),
                _validate_with_key(self.fields[7], result.val),
                _validate_with_key(self.fields[8], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )


class Dict10KeysValidator(
    Generic[A, B, C, D, E, F, G, H, I, J, Ret],
    Validator[Any, Ret, JSONValue],
):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        field6: KeyValidator[F],
        field7: KeyValidator[G],
        field8: KeyValidator[H],
        field9: KeyValidator[I],
        field10: KeyValidator[J],
        *,
        into: Callable[[A, B, C, D, E, F, G, H, I, J], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            field8,
            field9,
            field10,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        # ok, not sure why this works, but {f.key for f in self.fields} doesn't
        result = _dict_without_extra_keys(
            {self.fields[x][0] for x in range(len(self.fields))}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                _validate_with_key(self.fields[0], result.val),
                _validate_with_key(self.fields[1], result.val),
                _validate_with_key(self.fields[2], result.val),
                _validate_with_key(self.fields[3], result.val),
                _validate_with_key(self.fields[4], result.val),
                _validate_with_key(self.fields[5], result.val),
                _validate_with_key(self.fields[6], result.val),
                _validate_with_key(self.fields[7], result.val),
                _validate_with_key(self.fields[8], result.val),
                _validate_with_key(self.fields[9], result.val),
                self.into,
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_jo_dict)
            )
