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
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Pattern,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from koda import compose, mapping_get, safe_try
from koda.either import Either, Either3, First, Second, Third
from koda.maybe import Just, Maybe, Nothing, nothing
from koda.result import Err, Ok, Result

from koda_validate._cruft import _flat_map_same_type_if_not_none, _typed_tuple
from koda_validate.serialization import JsonSerializable
from koda_validate.typedefs import (
    JO,
    PredicateValidator,
    PredicateValidatorJO,
    TransformableValidator,
    Validator,
)
from koda_validate.utils import accum_errors, expected, unwrap_jsonable, validate_and_map

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


@dataclass(frozen=True)
class MaxLength(PredicateValidatorJO[str]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) <= self.length

    def err_message_str(self, val: str) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinLength(PredicateValidatorJO[str]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: str) -> bool:
        return len(val) >= self.length

    def err_message_str(self, val: str) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MinItems(PredicateValidatorJO[List[Any]]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) >= self.length

    def err_message_str(self, val: List[Any]) -> str:
        return f"minimum allowed length is {self.length}"


@dataclass(frozen=True)
class MaxItems(PredicateValidatorJO[List[Any]]):
    length: int

    def __post_init__(self) -> None:
        assert self.length >= 0

    def is_valid(self, val: List[Any]) -> bool:
        return len(val) <= self.length

    def err_message_str(self, val: List[Any]) -> str:
        return f"maximum allowed length is {self.length}"


@dataclass(frozen=True)
class MinProperties(PredicateValidatorJO[Dict[Any, Any]]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err_message_str(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxProperties(PredicateValidatorJO[Dict[Any, Any]]):
    size: int

    def __post_init__(self) -> None:
        assert self.size >= 0

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err_message_str(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


class UniqueItems(PredicateValidatorJO[List[Any]]):
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

    def err_message_str(self, val: List[Any]) -> str:
        return "all items must be unique"


unique_items = UniqueItems()


class Boolean(TransformableValidator[Any, bool, JO]):
    def __init__(self, *validators: PredicateValidator[bool, JO]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[bool, JO]:
        if isinstance(val, bool):
            return accum_errors(val, self.validators).map_err(JO)
        else:
            return err([expected("a boolean")])


class String(TransformableValidator[Any, str, JO]):
    def __init__(self, *validators: PredicateValidator[str, JO]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[str, JO]:
        if isinstance(val, str):
            return accum_errors(val, self.validators).map_err(JO)
        else:
            return err([expected("a string")])


@dataclass(frozen=True)
class RegexValidator(PredicateValidatorJO[str]):
    pattern: Pattern[str]

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message_str(self, val: str) -> str:
        return rf"must match pattern {self.pattern.pattern}"


@dataclass(frozen=True)
class Email(PredicateValidatorJO[str]):
    pattern: Pattern[str] = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")

    def is_valid(self, val: str) -> bool:
        return re.match(self.pattern, val) is not None

    def err_message_str(self, val: str) -> str:
        return "expected a valid email address"


class Integer(TransformableValidator[Any, int, JO]):
    def __init__(self, *validators: PredicateValidator[int, JO]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[int, JO]:
        # can't use isinstance because it would return true for bools
        if type(val) == int:
            return accum_errors(val, self.validators).map_err(JO)
        else:
            return err([expected("an integer")])


class Float(TransformableValidator[Any, float, JO]):
    def __init__(self, *validators: PredicateValidator[float, JO]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[float, JO]:
        if isinstance(val, float):
            return accum_errors(val, self.validators).map_err(JO)
        else:
            return err([expected("a float")])


class Decimal(TransformableValidator[Any, DecimalStdLib, JO]):
    def __init__(self, *validators: PredicateValidator[DecimalStdLib, JO]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[DecimalStdLib, JO]:
        expected_msg = expected("a decimal-compatible string or integer")
        if isinstance(val, DecimalStdLib):
            return Ok(val)
        elif isinstance(val, (str, int)):
            try:
                return Ok(DecimalStdLib(val))
            except decimal.InvalidOperation:
                return err([expected_msg])
        else:
            return err([expected_msg])


def _safe_try_int(val: Any) -> Result[int, Exception]:
    return safe_try(int, val)


class Date(TransformableValidator[Any, date, JO]):
    """
    Expects dates to be yyyy-mm-dd
    """

    def __init__(self, *validators: PredicateValidator[date, JO]) -> None:
        self.validators = validators

    def __call__(self, val: Any) -> Result[date, JO]:
        fail_msg = err(["expected date formatted as yyyy-mm-dd"])
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
                    return accum_errors(result.val, self.validators).map_err(JO)
        else:
            return fail_msg


class MapOf(TransformableValidator[Any, Dict[A, B], JO]):
    """
    Note that while a key should always be expected to be received as a string,
    it's possible that we may want to validate and cast it to a different
    type (i.e. a date)
    """

    def __init__(
        self,
        key_validator: TransformableValidator[Any, A, JO],
        value_validator: TransformableValidator[Any, B, JO],
        *dict_validators: PredicateValidator[Dict[A, B], JO],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.dict_validators = dict_validators

    def __call__(self, data: Any) -> Result[Dict[A, B], JO]:
        if isinstance(data, dict):
            return_dict: Dict[A, B] = {}
            errors: Dict[str, JO] = {}
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

            dict_validator_errors: List[JO] = []
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

                errors[OBJECT_ERRORS_FIELD] = JO(dict_validator_errors)

            if errors:
                return err(errors)
            else:
                return Ok(return_dict)
        else:
            return err({"invalid type": [expected("a map")]})


class ArrayOf(TransformableValidator[Any, List[A], JO]):
    def __init__(
        self,
        item_validator: TransformableValidator[Any, A, JO],
        *list_validators: PredicateValidator[List[Any], JO],
    ) -> None:
        self.item_validator = item_validator
        self.list_validators = list_validators

    def __call__(self, val: Any) -> Result[List[A], JO]:
        if isinstance(val, list):
            return_list: List[A] = []
            errors: Dict[str, JO] = {}

            list_errors: List[JO] = []
            for validator in self.list_validators:
                result = validator(val)

                if isinstance(result, Err):
                    list_errors.append(result.val)

            if len(list_errors) > 0:
                errors["__array__"] = JO(list_errors)

            for i, item in enumerate(val):
                item_result = self.item_validator(item)
                if isinstance(item_result, Ok):
                    return_list.append(item_result.val)
                else:
                    errors[f"index {i}"] = item_result.val

            if len(errors) > 0:
                return err(errors)
            else:
                return Ok(return_list)
        else:
            return err({"invalid type": [expected("an array")]})


EnumT = TypeVar("EnumT", str, int)


class Lazy(TransformableValidator[A, Ret, JO]):
    def __init__(
        self,
        validator: Callable[[], TransformableValidator[A, Ret, JO]],
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

    def __call__(self, data: A) -> Result[Ret, JO]:
        return self.validator()(data)


class Enum(PredicateValidatorJO[EnumT]):
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


def err(
    val: Union[
        str,
        int,
        float,
        bool,
        None,
        List["JO"],
        Tuple["JO", ...],
        Dict[str, "JO"],
        # until we have recursive types, we should at least make
        # it easy to create common types of error messages without needing to always
        # use `Jsonable`
        Dict[str, str],
        Dict[str, List[str]],
        List[str],
    ]
) -> Err[JO]:
    if isinstance(val, dict):
        ret: Dict[str, JO] = {}
        for k, v in val.items():
            if isinstance(v, JO):
                ret[k] = v
            elif isinstance(v, list):
                list_v: List[JO] = []
                for item in v:
                    if isinstance(item, JO):
                        list_v.append(item)
                    else:
                        list_v.append(JO(item))
                ret[k] = JO(list_v)
            else:
                ret[k] = JO(v)
        return Err(JO(ret))
    elif isinstance(val, list):
        return Err(JO([item if isinstance(item, JO) else JO(item) for item in val]))
    else:
        return Err(JO(val))


KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, JO]]]


def _validate_with_key(
    r: KeyValidator[A], data: Dict[Any, Any]
) -> Result[A, Tuple[str, JO]]:
    key, fn = r

    def add_key(val: JO) -> Tuple[str, JO]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)


class IsObject(TransformableValidator[Any, Dict[Any, Any], JO]):
    def __call__(self, val: Any) -> Result[Dict[Any, Any], JO]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return err({OBJECT_ERRORS_FIELD: [expected("an object")]})


def _dict_without_extra_keys(keys: Set[str], data: Any) -> Result[Dict[Any, Any], JO]:
    return IsObject()(data).flat_map(_has_no_extra_keys(keys))


class OneOf2(TransformableValidator[Any, Either[A, B], JO]):
    def __init__(
        self,
        variant_one: Union[
            TransformableValidator[Any, A, JO],
            Tuple[str, TransformableValidator[Any, A, JO]],
        ],
        variant_two: Union[
            TransformableValidator[Any, B, JO],
            Tuple[str, TransformableValidator[Any, B, JO]],
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

    def __call__(self, val: Any) -> Result[Either[A, B], JO]:
        v1_result = self.variant_one(val)

        if isinstance(v1_result, Ok):
            return Ok(First(v1_result.val))
        else:
            v2_result = self.variant_two(val)

            if isinstance(v2_result, Ok):
                return Ok(Second(v2_result.val))
            else:
                return err(
                    {
                        self.variant_one_label: v1_result.val,
                        self.variant_two_label: v2_result.val,
                    }
                )


class OneOf3(TransformableValidator[Any, Either3[A, B, C], JO]):
    def __init__(
        self,
        variant_one: Union[
            TransformableValidator[Any, A, JO],
            Tuple[str, TransformableValidator[Any, A, JO]],
        ],
        variant_two: Union[
            TransformableValidator[Any, B, JO],
            Tuple[str, TransformableValidator[Any, B, JO]],
        ],
        variant_three: Union[
            TransformableValidator[Any, C, JO],
            Tuple[str, TransformableValidator[Any, C, JO]],
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

    def __call__(self, val: Any) -> Result[Either3[A, B, C], JO]:
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
                    return err(
                        {
                            self.variant_one_label: v1_result.val,
                            self.variant_two_label: v2_result.val,
                            self.variant_three_label: v3_result.val,
                        }
                    )


def _tuple_to_dict_errors(errs: Tuple[JO, ...]) -> Dict[str, JO]:
    return {f"index {i}": err for i, err in enumerate(errs)}


class Tuple2(TransformableValidator[Any, Tuple[A, B], JO]):
    required_length: int = 2

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, JO]],
        slot2_validator: Callable[[Any], Result[B, JO]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B]], Result[Tuple[A, B], JO]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B], JO]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B], Tuple[JO, ...]] = validate_and_map(
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
                _typed_tuple,
            )

            if isinstance(result, Err):
                return result.map_err(compose(_tuple_to_dict_errors, JO))
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return err(
                {"invalid type": [f"expected array of length {self.required_length}"]}
            )


class Tuple3(TransformableValidator[Any, Tuple[A, B, C], JO]):
    required_length: int = 3

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, JO]],
        slot2_validator: Callable[[Any], Result[B, JO]],
        slot3_validator: Callable[[Any], Result[C, JO]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B, C]], Result[Tuple[A, B, C], JO]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B, C], JO]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B, C], Tuple[JO, ...]] = validate_and_map(
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
                self.slot3_validator(data[2]),
                _typed_tuple,
            )

            if isinstance(result, Err):
                return result.map_err(compose(_tuple_to_dict_errors, JO))
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return err(
                {"invalid type": [f"expected array of length {self.required_length}"]}
            )


def _has_no_extra_keys(keys: Set[str]) -> Validator[Dict[A, B], Dict[A, B], JO]:
    def inner(mapping: Dict[A, B]) -> Result[Dict[A, B], JO]:
        if len(mapping.keys() - keys) > 0:
            return err(
                {
                    OBJECT_ERRORS_FIELD: [
                        f"Received unknown keys. Only expected {sorted(keys)}"
                    ]
                }
            )
        else:
            return Ok(mapping)

    return inner


BLANK_STRING_MSG: Final[JO] = JO("cannot be blank")


class NotBlank(PredicateValidator[str, JO]):
    def is_valid(self, val: str) -> bool:
        return len(val.strip()) != 0

    def err_message(self, val: str) -> JO:
        return BLANK_STRING_MSG


not_blank = NotBlank()

_KEY_MISSING: Final[str] = "key missing"


class RequiredField(Generic[A]):
    def __init__(self, validator: TransformableValidator[Any, A, JO]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, JO]:
        if isinstance(maybe_val, Nothing):
            return err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


class MaybeField(Generic[A]):
    def __init__(self, validator: TransformableValidator[Any, A, JO]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], JO]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], JO] = self.validator(maybe_val.val).map(Just)
        else:
            result = Ok(maybe_val)
        return result


def deserialize_and_validate(
    validator: TransformableValidator[Any, A, JO], data: AnyStr
) -> Result[A, JsonSerializable]:
    try:
        deserialized = loads(data)
    except Exception:
        return Err({"bad data": "invalid json"})
    else:
        return validator(deserialized).map_err(unwrap_jsonable)


class Nullable(TransformableValidator[Any, Maybe[A], JO]):
    """
    We have a value for a key, but it can be null (None)
    """

    def __init__(self, validator: TransformableValidator[Any, A, JO]) -> None:
        self.validator = validator

    def __call__(self, val: Optional[Any]) -> Result[Maybe[A], JO]:
        if val is None:
            return Ok(nothing)
        else:
            return self.validator(val).map(lambda x: Just(x))


Num = TypeVar("Num", int, float, DecimalStdLib)


@dataclass(frozen=True)
class Minimum(PredicateValidatorJO[Num]):
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
class Maximum(PredicateValidatorJO[Num]):
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
class MultipleOf(PredicateValidatorJO[Num]):
    factor: Num

    def is_valid(self, val: Num) -> bool:
        return val % self.factor == 0

    def err_message_str(self, val: Num) -> str:
        return f"expected multiple of {self.factor}"


class NullType(TransformableValidator[Any, None, JO]):
    def __call__(self, val: Any) -> Result[None, JO]:
        if val is None:
            return Ok(val)
        else:
            return err([expected("null")])


Null = NullType()


def prop(
    prop_: str, validator: TransformableValidator[Any, A, JO]
) -> Tuple[str, Callable[[Any], Result[A, JO]]]:
    return prop_, RequiredField(validator)


def maybe_prop(
    prop_: str, validator: TransformableValidator[Any, A, JO]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], JO]]]:
    return prop_, MaybeField(validator)


def _tuples_to_jo_dict(data: Tuple[Tuple[str, JO], ...]) -> JO:
    return JO(dict(data))


class Obj1Prop(Generic[A, Ret], TransformableValidator[Any, Ret, JO]):
    def __init__(
        self,
        field1: KeyValidator[A],
        *,
        into: Callable[[A], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
    ) -> None:
        self.fields = (field1,)
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JO]:
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


class Obj2Props(Generic[A, B, Ret], TransformableValidator[Any, Ret, JO]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        *,
        into: Callable[[A, B], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JO]:
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


class Obj3Props(Generic[A, B, C, Ret], TransformableValidator[Any, Ret, JO]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        *,
        into: Callable[[A, B, C], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JO]:
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


class Obj4Props(Generic[A, B, C, D, Ret], TransformableValidator[Any, Ret, JO]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        *,
        into: Callable[[A, B, C, D], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
    ) -> None:
        self.fields = (
            field1,
            field2,
            field3,
            field4,
        )
        self.into = into
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JO]:
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


class Obj5Props(Generic[A, B, C, D, E, Ret], TransformableValidator[Any, Ret, JO]):
    def __init__(
        self,
        field1: KeyValidator[A],
        field2: KeyValidator[B],
        field3: KeyValidator[C],
        field4: KeyValidator[D],
        field5: KeyValidator[E],
        *,
        into: Callable[[A, B, C, D, E], Ret],
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JO]:
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


class Obj6Props(Generic[A, B, C, D, E, F, Ret], TransformableValidator[Any, Ret, JO]):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JO]:
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


class Obj7Props(Generic[A, B, C, D, E, F, G, Ret], TransformableValidator[Any, Ret, JO]):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JO]:
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
    Generic[A, B, C, D, E, F, G, H, Ret], TransformableValidator[Any, Ret, JO]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JO]:
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
    Generic[A, B, C, D, E, F, G, H, I, Ret], TransformableValidator[Any, Ret, JO]
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JO]:
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
    TransformableValidator[Any, Ret, JO],
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JO]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JO]:
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
