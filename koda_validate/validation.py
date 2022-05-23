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
from koda.either import Either, Either3, First, Second, Third
from koda.maybe import Just, Maybe, Nothing, nothing
from koda.result import Err, Ok, Result

from koda_validate._cruft import _flat_map_same_type_if_not_none, _typed_tuple
from koda_validate.typedefs import (
    Jsonish,
    PredicateValidator,
    PredicateValidatorJson,
    TransformableValidator,
    Validator,
)
from koda_validate.utils import accum_errors, expected, validate_and_map

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")
H = TypeVar("H")
I = TypeVar("I")
J = TypeVar("J")
K = TypeVar("K")
L = TypeVar("L")

Ret = TypeVar("Ret")

FailT = TypeVar("FailT")

OBJECT_ERRORS_FIELD: Final[str] = "__object__"


def accum_errors_jsonish(
    val: A, validators: Iterable[PredicateValidator[A, Jsonish]]
) -> Result[A, Jsonish]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return cast(Result[A, Jsonish], accum_errors(val, validators))


@dataclass(frozen=True)
class MaxLength(PredicateValidatorJson[str]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err_message_str(self, val: str) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinLength(PredicateValidatorJson[str]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err_message_str(self, val: str) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MinItems(PredicateValidatorJson[list[Any]]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: list[Any]) -> bool:
        return len(val) >= self.length

    def err_message_str(self, val: list[Any]) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MaxItems(PredicateValidatorJson[list[Any]]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: list[Any]) -> bool:
        return len(val) <= self.length

    def err_message_str(self, val: list[Any]) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinProperties(PredicateValidatorJson[dict[Any, Any]]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err_message_str(self, val: dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxProperties(PredicateValidatorJson[dict[Any, Any]]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err_message_str(self, val: dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


class UniqueItems(PredicateValidatorJson[list[Any]]):
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


class Boolean(TransformableValidator[Any, bool, Jsonish]):
    def __init__(self, *validators: PredicateValidator[bool, Jsonish]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[bool, Jsonish]:
        if isinstance(val, bool):
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("a boolean")])


class String(TransformableValidator[Any, str, Jsonish]):
    def __init__(self, *validators: PredicateValidator[str, Jsonish]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[str, Jsonish]:
        if isinstance(val, str):
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("a string")])


@dataclass(frozen=True)
class RegexValidator(PredicateValidatorJson[str]):
    pattern: Pattern[str]

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message_str(self, val: str) -> str:
        return rf"must match pattern {self.pattern.pattern}"


@dataclass(frozen=True)
class Email(PredicateValidatorJson[str]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message_str(self, val: str) -> str:
        return "expected a valid email address"


class Integer(TransformableValidator[Any, int, Jsonish]):
    def __init__(self, *validators: PredicateValidator[int, Jsonish]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[int, Jsonish]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("an integer")])


class Float(TransformableValidator[Any, float, Jsonish]):
    def __init__(self, *validators: PredicateValidator[float, Jsonish]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[float, Jsonish]:
        if isinstance(val, float):
            return accum_errors_jsonish(val, self.validators)
        else:
            return Err([expected("a float")])


class Decimal(TransformableValidator[Any, DecimalStdLib, Jsonish]):
    def __init__(self, *validators: PredicateValidator[DecimalStdLib, Jsonish]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[DecimalStdLib, Jsonish]:
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


class Date(TransformableValidator[Any, date, Jsonish]):
    """
    Expects dates to be yyyy-mm-dd
    """

    def __init__(self, *validators: PredicateValidator[date, Jsonish]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[date, Jsonish]:
        fail_msg: Result[date, Jsonish] = Err(["expected date formatted as yyyy-mm-dd"])
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


class MapOf(TransformableValidator[Any, dict[A, B], Jsonish]):
    """
    Note that while a key should always be expected to be received as a string,
    it's possible that we may want to validate and cast it to a different
    type (i.e. a date)
    """

    def __init__(
        self,
        key_validator: TransformableValidator[Any, A, Jsonish],
        value_validator: TransformableValidator[Any, B, Jsonish],
        *dict_validators: PredicateValidator[dict[A, B], Jsonish],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.dict_validators = dict_validators

    def __call__(self, data: Any) -> Result[dict[A, B], Jsonish]:
        if isinstance(data, dict):
            return_dict: dict[A, B] = {}
            errors: dict[str, Jsonish] = {}
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

            dict_validator_errors: list[Jsonish] = []
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


class ArrayOf(TransformableValidator[Any, list[A], Jsonish]):
    def __init__(
        self,
        item_validator: TransformableValidator[Any, A, Jsonish],
        *list_validators: PredicateValidator[list[Any], Jsonish],
    ) -> None:
        self.item_validator = item_validator
        self.list_validators = list_validators

    def __call__(self, val: Any) -> Result[list[A], Jsonish]:
        if isinstance(val, list):
            return_list: list[A] = []
            errors: dict[str, Jsonish] = {}

            list_errors: list[Jsonish] = []
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


class Lazy(TransformableValidator[A, Ret, Jsonish]):
    def __init__(
        self,
        validator: Callable[[], TransformableValidator[A, Ret, Jsonish]],
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

    def __call__(self, data: A) -> Result[Ret, Jsonish]:
        return self.validator()(data)


# todo rename
class Enum(PredicateValidatorJson[EnumT]):
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


KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, Jsonish]]]


def _validate_with_key(
    r: KeyValidator[A], data: dict[Any, Any]
) -> Result[A, Tuple[str, Jsonish]]:
    key, fn = r

    def add_key(val: Jsonish) -> Tuple[str, Jsonish]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)


class IsObject(TransformableValidator[Any, dict[Any, Any], Jsonish]):
    def __call__(self, val: Any) -> Result[dict[Any, Any], Jsonish]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return Err({OBJECT_ERRORS_FIELD: [expected("an object")]})


def _dict_without_extra_keys(
    keys: Set[str], data: Any
) -> Result[dict[Any, Any], Jsonish]:
    return IsObject()(data).flat_map(_has_no_extra_keys(keys))


class OneOf2(TransformableValidator[Any, Either[A, B], Jsonish]):
    def __init__(
        self,
        variant_one: Union[
            TransformableValidator[Any, A, Jsonish],
            Tuple[str, TransformableValidator[Any, A, Jsonish]],
        ],
        variant_two: Union[
            TransformableValidator[Any, B, Jsonish],
            Tuple[str, TransformableValidator[Any, B, Jsonish]],
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

    def __call__(self, val: Any) -> Result[Either[A, B], Jsonish]:
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


class OneOf3(TransformableValidator[Any, Either3[A, B, C], Jsonish]):
    def __init__(
        self,
        variant_one: Union[
            TransformableValidator[Any, A, Jsonish],
            Tuple[str, TransformableValidator[Any, A, Jsonish]],
        ],
        variant_two: Union[
            TransformableValidator[Any, B, Jsonish],
            Tuple[str, TransformableValidator[Any, B, Jsonish]],
        ],
        variant_three: Union[
            TransformableValidator[Any, C, Jsonish],
            Tuple[str, TransformableValidator[Any, C, Jsonish]],
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

    def __call__(self, val: Any) -> Result[Either3[A, B, C], Jsonish]:
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


def _tuple_to_dict_errors(errs: Tuple[Jsonish, ...]) -> dict[str, Jsonish]:
    return {f"index {i}": err for i, err in enumerate(errs)}


class Tuple2(TransformableValidator[Any, Tuple[A, B], Jsonish]):
    required_length: int = 2

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, Jsonish]],
        slot2_validator: Callable[[Any], Result[B, Jsonish]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B]], Result[Tuple[A, B], Jsonish]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B], Jsonish]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B], Tuple[Jsonish, ...]] = validate_and_map(
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


class Tuple3(TransformableValidator[Any, Tuple[A, B, C], Jsonish]):
    required_length: int = 3

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, Jsonish]],
        slot2_validator: Callable[[Any], Result[B, Jsonish]],
        slot3_validator: Callable[[Any], Result[C, Jsonish]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B, C]], Result[Tuple[A, B, C], Jsonish]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B, C], Jsonish]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B, C], Tuple[Jsonish, ...]] = validate_and_map(
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


def _has_no_extra_keys(keys: Set[str]) -> Validator[dict[A, B], dict[A, B], Jsonish]:
    def inner(mapping: dict[A, B]) -> Result[dict[A, B], Jsonish]:
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


class NotBlank(PredicateValidator[str, Jsonish]):
    def is_valid(self, val: str) -> bool:
        return len(val.strip()) != 0

    def err_message(self, val: str) -> Jsonish:
        return BLANK_STRING_MSG


not_blank = NotBlank()

_KEY_MISSING: Final[str] = "key missing"


class RequiredField(Generic[A]):
    def __init__(self, validator: TransformableValidator[Any, A, Jsonish]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, Jsonish]:
        if isinstance(maybe_val, Nothing):
            return Err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


class MaybeField(Generic[A]):
    def __init__(self, validator: TransformableValidator[Any, A, Jsonish]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Jsonish]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], Jsonish] = self.validator(maybe_val.val).map(
                _to_just
            )
        else:
            result = Ok(maybe_val)
        return result


def deserialize_and_validate(
    validator: TransformableValidator[Any, A, Jsonish], data: AnyStr
) -> Result[A, Jsonish]:
    try:
        deserialized = loads(data)
    except Exception:
        return Err({"bad data": "invalid json"})
    else:
        return validator(deserialized)


def _to_just(x: A) -> Maybe[A]:
    """
    for pyright, as of 1.1.246
    """
    return Just(x)


def _variant_errors(*variants: Jsonish) -> Jsonish:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


class Nullable(TransformableValidator[Any, Maybe[A], Jsonish]):
    """
    We have a value for a key, but it can be null (None)
    """

    def __init__(self, validator: TransformableValidator[Any, A, Jsonish]) -> None:
        self.validator = validator

    def __call__(self, val: Optional[Any]) -> Result[Maybe[A], Jsonish]:
        if val is None:
            return Ok(nothing)
        else:
            result: Result[A, Jsonish] = self.validator(val)
            if isinstance(result, Ok):
                return result.map(_to_just)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )


Num = TypeVar("Num", int, float, DecimalStdLib)


@dataclass(frozen=True)
class Minimum(PredicateValidatorJson[Num]):
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
class Maximum(PredicateValidatorJson[Num]):
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
class MultipleOf(PredicateValidatorJson[Num]):
    factor: Num

    def is_valid(self, val: Num) -> bool:
        return val % self.factor == 0

    def err_message_str(self, val: Num) -> str:
        return f"expected multiple of {self.factor}"


class NullType(TransformableValidator[Any, None, Jsonish]):
    def __call__(self, val: Any) -> Result[None, Jsonish]:
        if val is None:
            return Ok(val)
        else:
            return Err([expected("null")])


Null = NullType()


def prop(
    prop_: str, validator: TransformableValidator[Any, A, Jsonish]
) -> Tuple[str, Callable[[Any], Result[A, Jsonish]]]:
    return prop_, RequiredField(validator)


def maybe_prop(
    prop_: str, validator: TransformableValidator[Any, A, Jsonish]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], Jsonish]]]:
    return prop_, MaybeField(validator)


def _tuples_to_jo_dict(data: Tuple[Tuple[str, Jsonish], ...]) -> Jsonish:
    return dict(data)


class Obj1Prop(Generic[A, Ret], TransformableValidator[Any, Ret, Jsonish]):
    def __init__(
        self,
        field1: KeyValidator[A],
        *,
        into: Callable[[A], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
    ) -> None:
        self.fields = (field1,)
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj2Props(Generic[A, B, Ret], TransformableValidator[Any, Ret, Jsonish]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        *,
        into: Callable[[A, B], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj3Props(Generic[A, B, C, Ret], TransformableValidator[Any, Ret, Jsonish]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        *,
        into: Callable[[A, B, C], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj4Props(Generic[A, B, C, D, Ret], TransformableValidator[Any, Ret, Jsonish]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        *,
        into: Callable[[A, B, C, D], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj5Props(Generic[A, B, C, D, E, Ret], TransformableValidator[Any, Ret, Jsonish]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        *,
        into: Callable[[A, B, C, D, E], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj6Props(
    Generic[A, B, C, D, E, F, Ret], TransformableValidator[Any, Ret, Jsonish]
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj7Props(
    Generic[A, B, C, D, E, F, G, Ret], TransformableValidator[Any, Ret, Jsonish]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj8Props(
    Generic[A, B, C, D, E, F, G, H, Ret], TransformableValidator[Any, Ret, Jsonish]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj9Props(
    Generic[A, B, C, D, E, F, G, H, I, Ret], TransformableValidator[Any, Ret, Jsonish]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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


class Obj10Props(
    Generic[A, B, C, D, E, F, G, H, I, J, Ret],
    TransformableValidator[Any, Ret, Jsonish],
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
        validate_object: Optional[Callable[[Ret], Result[Ret, Jsonish]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, Jsonish]:
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
