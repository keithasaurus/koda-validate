from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

from koda import Err, Just, Maybe, Nothing, Ok, Result, mapping_get

from koda_validate._generics import A
from koda_validate.typedefs import Predicate, Serializable, Validator
from koda_validate.utils import OBJECT_ERRORS_FIELD, expected

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
T10 = TypeVar("T10")
T11 = TypeVar("T11")
T12 = TypeVar("T12")
T13 = TypeVar("T13")
T14 = TypeVar("T14")
T15 = TypeVar("T15")
T16 = TypeVar("T16")
T17 = TypeVar("T17")
T18 = TypeVar("T18")
T19 = TypeVar("T19")
T20 = TypeVar("T20")
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


_KEY_MISSING: Final[str] = "key missing"

KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, Serializable]]]

_is_dict_validation_err: Final[Dict[str, Serializable]] = {
    OBJECT_ERRORS_FIELD: [expected("a dictionary")]
}


def too_many_keys(keys: set[str]) -> Err[Serializable]:
    return Err(
        {OBJECT_ERRORS_FIELD: [f"Received unknown keys. Only expected {sorted(keys)}"]}
    )


def _validate_and_map(
    into: Callable[..., Ret],
    data: Any,
    # this could be handled better with variadic generics
    *fields: KeyValidator[Any],
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Result[Ret, Serializable]:
    allowed_keys = {k for k, _ in fields}
    if not isinstance(data, dict):
        return Err(_is_dict_validation_err)
    if len(data.keys() - allowed_keys) > 0:
        return too_many_keys(allowed_keys)

    args = []
    errs: List[Tuple[str, Serializable]] = []
    for key, validator in fields:
        result = validator(mapping_get(data, key))

        # (slightly) optimized for no .map_err call
        if isinstance(result, Err):
            errs.append((key, result.val))
        else:
            args.append(result.val)

    if len(errs) > 0:
        return Err(_tuples_to_json_dict(errs))
    else:
        obj = into(*args)
        if validate_object is None:
            return Ok(obj)
        else:
            return validate_object(obj)


@dataclass(frozen=True)
class RequiredField(Generic[A]):
    validator: Validator[Any, A, Serializable]

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, Serializable]:
        if isinstance(maybe_val, Nothing):
            return Err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


@dataclass(frozen=True)
class MaybeField(Generic[A]):
    validator: Validator[Any, A, Serializable]

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Serializable]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], Serializable] = self.validator(maybe_val.val).map(
                Just
            )
        else:
            result = Ok(maybe_val)
        return result


def key(
    prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[A, Serializable]]]:
    return prop_, RequiredField(validator)


def maybe_key(
    prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], Serializable]]]:
    return prop_, MaybeField(validator)


@dataclass(init=False)
class MapValidator(Validator[Any, Dict[T1, T2], Serializable]):
    key_validator: Validator[Any, T1, Serializable]
    value_validator: Validator[Any, T2, Serializable]
    predicates: Tuple[Predicate[Dict[T1, T2], Serializable], ...]

    def __init__(
        self,
        key_validator: Validator[Any, T1, Serializable],
        value_validator: Validator[Any, T2, Serializable],
        *predicates: Predicate[Dict[T1, T2], Serializable],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.predicates = predicates

    def __call__(self, data: Any) -> Result[Dict[T1, T2], Serializable]:
        if isinstance(data, dict):
            return_dict: Dict[T1, T2] = {}
            errors: Dict[str, Serializable] = {}
            for key, val in data.items():
                key_result = self.key_validator(key)
                val_result = self.value_validator(val)

                if isinstance(key_result, Ok) and isinstance(val_result, Ok):
                    return_dict[key_result.val] = val_result.val
                else:
                    err_key = str(key)
                    if isinstance(key_result, Err):
                        errors[err_key] = {"key_error": key_result.val}

                    if isinstance(val_result, Err):
                        err_dict = {"value_error": val_result.val}
                        errs: Maybe[Serializable] = mapping_get(errors, err_key)
                        if isinstance(errs, Just) and isinstance(errs.val, dict):
                            errs.val.update(err_dict)
                        else:
                            errors[err_key] = err_dict

            dict_validator_errors: List[Serializable] = []
            for predicate in self.predicates:
                # Note that the expectation here is that validators will likely
                # be doing json like number of keys; they aren't expected
                # to be drilling down into specific keys and values. That may be
                # an incorrect assumption; if so, some minor refactoring is probably
                # necessary.
                result = predicate(data)
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
            return Err({OBJECT_ERRORS_FIELD: [expected("a map")]})


class IsDictValidator(Validator[Any, Dict[Any, Any], Serializable]):
    def __call__(self, val: Any) -> Result[Dict[Any, Any], Serializable]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return Err(_is_dict_validation_err)


is_dict_validator = IsDictValidator()


def _dict_without_extra_keys(
    keys: Set[str], data: Any
) -> Optional[Dict[str, Serializable]]:
    """
    We're returning Optional here because it's faster than Ok/Err,
    and this is just a private function
    """
    if isinstance(data, dict):
        # this seems to be faster than `for key_ in data.keys()`
        for key_ in data:
            if key_ not in keys:
                return {
                    OBJECT_ERRORS_FIELD: [
                        f"Received unknown keys. Only expected {sorted(keys)}"
                    ]
                }
        return None
    else:
        return _is_dict_validation_err


@dataclass(frozen=True)
class MinKeys(Predicate[Dict[Any, Any], Serializable]):
    size: int

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) >= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"minimum allowed properties is {self.size}"


@dataclass(frozen=True)
class MaxKeys(Predicate[Dict[Any, Any], Serializable]):
    size: int

    def is_valid(self, val: Dict[Any, Any]) -> bool:
        return len(val) <= self.size

    def err(self, val: Dict[Any, Any]) -> str:
        return f"maximum allowed properties is {self.size}"


def _tuples_to_json_dict(data: List[Tuple[str, Serializable]]) -> Serializable:
    return dict(data)


class Dict1KeysValidator(Generic[T1, Ret], Validator[Any, Ret, Serializable]):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1], Ret],
        field1: KeyValidator[T1],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (field1,)
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict2KeysValidator(Generic[T1, T2, Ret], Validator[Any, Ret, Serializable]):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict3KeysValidator(Generic[T1, T2, T3, Ret], Validator[Any, Ret, Serializable]):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict4KeysValidator(Generic[T1, T2, T3, T4, Ret], Validator[Any, Ret, Serializable]):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
            field4,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict5KeysValidator(
    Generic[T1, T2, T3, T4, T5, Ret], Validator[Any, Ret, Serializable]
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict6KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, Ret], Validator[Any, Ret, Serializable]
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict7KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, Ret], Validator[Any, Ret, Serializable]
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict8KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, Ret], Validator[Any, Ret, Serializable]
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            field8,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict9KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, Ret], Validator[Any, Ret, Serializable]
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict10KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict11KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict12KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict13KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict14KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict15KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        field15: KeyValidator[T15],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
            field15,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict16KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, Ret],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16], Ret
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        field15: KeyValidator[T15],
        field16: KeyValidator[T16],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict17KeysValidator(
    Generic[
        T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, Ret
    ],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17],
            Ret,
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        field15: KeyValidator[T15],
        field16: KeyValidator[T16],
        field17: KeyValidator[T17],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict18KeysValidator(
    Generic[
        T1,
        T2,
        T3,
        T4,
        T5,
        T6,
        T7,
        T8,
        T9,
        T10,
        T11,
        T12,
        T13,
        T14,
        T15,
        T16,
        T17,
        T18,
        Ret,
    ],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [
                T1,
                T2,
                T3,
                T4,
                T5,
                T6,
                T7,
                T8,
                T9,
                T10,
                T11,
                T12,
                T13,
                T14,
                T15,
                T16,
                T17,
                T18,
            ],
            Ret,
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        field15: KeyValidator[T15],
        field16: KeyValidator[T16],
        field17: KeyValidator[T17],
        field18: KeyValidator[T18],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            field18,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict19KeysValidator(
    Generic[
        T1,
        T2,
        T3,
        T4,
        T5,
        T6,
        T7,
        T8,
        T9,
        T10,
        T11,
        T12,
        T13,
        T14,
        T15,
        T16,
        T17,
        T18,
        T19,
        Ret,
    ],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [
                T1,
                T2,
                T3,
                T4,
                T5,
                T6,
                T7,
                T8,
                T9,
                T10,
                T11,
                T12,
                T13,
                T14,
                T15,
                T16,
                T17,
                T18,
                T19,
            ],
            Ret,
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        field15: KeyValidator[T15],
        field16: KeyValidator[T16],
        field17: KeyValidator[T17],
        field18: KeyValidator[T18],
        field19: KeyValidator[T19],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            field18,
            field19,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


class Dict20KeysValidator(
    Generic[
        T1,
        T2,
        T3,
        T4,
        T5,
        T6,
        T7,
        T8,
        T9,
        T10,
        T11,
        T12,
        T13,
        T14,
        T15,
        T16,
        T17,
        T18,
        T19,
        T20,
        Ret,
    ],
    Validator[Any, Ret, Serializable],
):
    __match_args__: Tuple[str, ...] = ("dv_fields",)

    def __init__(
        self,
        into: Callable[
            [
                T1,
                T2,
                T3,
                T4,
                T5,
                T6,
                T7,
                T8,
                T9,
                T10,
                T11,
                T12,
                T13,
                T14,
                T15,
                T16,
                T17,
                T18,
                T19,
                T20,
            ],
            Ret,
        ],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        field6: KeyValidator[T6],
        field7: KeyValidator[T7],
        field8: KeyValidator[T8],
        field9: KeyValidator[T9],
        field10: KeyValidator[T10],
        field11: KeyValidator[T11],
        field12: KeyValidator[T12],
        field13: KeyValidator[T13],
        field14: KeyValidator[T14],
        field15: KeyValidator[T15],
        field16: KeyValidator[T16],
        field17: KeyValidator[T17],
        field18: KeyValidator[T18],
        field19: KeyValidator[T19],
        field20: KeyValidator[T20],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            field18,
            field19,
            field20,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, Serializable]:
        return _validate_and_map(
            self.into, data, *self.dv_fields, validate_object=self.validate_object
        )


@overload
def dict_validator(
    into: Callable[[T1], Ret],
    field1: KeyValidator[T1],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret
    ],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    field15: KeyValidator[T15],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16], Ret
    ],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    field15: KeyValidator[T15],
    field16: KeyValidator[T16],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17], Ret
    ],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    field15: KeyValidator[T15],
    field16: KeyValidator[T16],
    field17: KeyValidator[T17],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18],
        Ret,
    ],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    field15: KeyValidator[T15],
    field16: KeyValidator[T16],
    field17: KeyValidator[T17],
    field18: KeyValidator[T18],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[
        [
            T1,
            T2,
            T3,
            T4,
            T5,
            T6,
            T7,
            T8,
            T9,
            T10,
            T11,
            T12,
            T13,
            T14,
            T15,
            T16,
            T17,
            T18,
            T19,
        ],
        Ret,
    ],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    field15: KeyValidator[T15],
    field16: KeyValidator[T16],
    field17: KeyValidator[T17],
    field18: KeyValidator[T18],
    field19: KeyValidator[T19],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


@overload
def dict_validator(
    into: Callable[
        [
            T1,
            T2,
            T3,
            T4,
            T5,
            T6,
            T7,
            T8,
            T9,
            T10,
            T11,
            T12,
            T13,
            T14,
            T15,
            T16,
            T17,
            T18,
            T19,
            T20,
        ],
        Ret,
    ],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    field5: KeyValidator[T5],
    field6: KeyValidator[T6],
    field7: KeyValidator[T7],
    field8: KeyValidator[T8],
    field9: KeyValidator[T9],
    field10: KeyValidator[T10],
    field11: KeyValidator[T11],
    field12: KeyValidator[T12],
    field13: KeyValidator[T13],
    field14: KeyValidator[T14],
    field15: KeyValidator[T15],
    field16: KeyValidator[T16],
    field17: KeyValidator[T17],
    field18: KeyValidator[T18],
    field19: KeyValidator[T19],
    field20: KeyValidator[T20],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:
    ...


def dict_validator(
    into: Union[
        Callable[[T1], Ret],
        Callable[[T1, T2], Ret],
        Callable[[T1, T2, T3], Ret],
        Callable[[T1, T2, T3, T4], Ret],
        Callable[[T1, T2, T3, T4, T5], Ret],
        Callable[[T1, T2, T3, T4, T5, T6], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret],
        Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16], Ret
        ],
        Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17],
            Ret,
        ],
        Callable[
            [
                T1,
                T2,
                T3,
                T4,
                T5,
                T6,
                T7,
                T8,
                T9,
                T10,
                T11,
                T12,
                T13,
                T14,
                T15,
                T16,
                T17,
                T18,
            ],
            Ret,
        ],
        Callable[
            [
                T1,
                T2,
                T3,
                T4,
                T5,
                T6,
                T7,
                T8,
                T9,
                T10,
                T11,
                T12,
                T13,
                T14,
                T15,
                T16,
                T17,
                T18,
                T19,
            ],
            Ret,
        ],
        Callable[
            [
                T1,
                T2,
                T3,
                T4,
                T5,
                T6,
                T7,
                T8,
                T9,
                T10,
                T11,
                T12,
                T13,
                T14,
                T15,
                T16,
                T17,
                T18,
                T19,
                T20,
            ],
            Ret,
        ],
    ],
    field1: KeyValidator[T1],
    field2: Optional[KeyValidator[T2]] = None,
    field3: Optional[KeyValidator[T3]] = None,
    field4: Optional[KeyValidator[T4]] = None,
    field5: Optional[KeyValidator[T5]] = None,
    field6: Optional[KeyValidator[T6]] = None,
    field7: Optional[KeyValidator[T7]] = None,
    field8: Optional[KeyValidator[T8]] = None,
    field9: Optional[KeyValidator[T9]] = None,
    field10: Optional[KeyValidator[T10]] = None,
    field11: Optional[KeyValidator[T11]] = None,
    field12: Optional[KeyValidator[T12]] = None,
    field13: Optional[KeyValidator[T13]] = None,
    field14: Optional[KeyValidator[T14]] = None,
    field15: Optional[KeyValidator[T15]] = None,
    field16: Optional[KeyValidator[T16]] = None,
    field17: Optional[KeyValidator[T17]] = None,
    field18: Optional[KeyValidator[T18]] = None,
    field19: Optional[KeyValidator[T19]] = None,
    field20: Optional[KeyValidator[T20]] = None,
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Serializable]]] = None,
) -> Validator[Any, Ret, Serializable]:

    if field2 is None:
        return Dict1KeysValidator(
            cast(Callable[[T1], Ret], into), field1, validate_object=validate_object
        )
    elif field3 is None:
        return Dict2KeysValidator(
            cast(Callable[[T1, T2], Ret], into),
            field1,
            field2,
            validate_object=validate_object,
        )

    elif field4 is None:
        return Dict3KeysValidator(
            cast(Callable[[T1, T2, T3], Ret], into),
            field1,
            field2,
            field3,
            validate_object=validate_object,
        )

    elif field5 is None:
        return Dict4KeysValidator(
            cast(Callable[[T1, T2, T3, T4], Ret], into),
            field1,
            field2,
            field3,
            field4,
            validate_object=validate_object,
        )

    elif field6 is None:
        return Dict5KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5], Ret], into),
            field1,
            field2,
            field3,
            field4,
            field5,
            validate_object=validate_object,
        )

    elif field7 is None:
        return Dict6KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5, T6], Ret], into),
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            validate_object=validate_object,
        )

    elif field8 is None:
        return Dict7KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5, T6, T7], Ret], into),
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            validate_object=validate_object,
        )

    elif field9 is None:
        return Dict8KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret], into),
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            field8,
            validate_object=validate_object,
        )

    elif field10 is None:
        return Dict9KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret], into),
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            field7,
            field8,
            field9,
            validate_object=validate_object,
        )

    elif field11 is None:
        return Dict10KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret], into),
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
            validate_object=validate_object,
        )

    elif field12 is None:
        return Dict11KeysValidator(
            cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret], into),
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
            field11,
            validate_object=validate_object,
        )

    elif field13 is None:
        return Dict12KeysValidator(
            cast(
                Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret], into
            ),
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
            field11,
            field12,
            validate_object=validate_object,
        )

    elif field14 is None:
        return Dict13KeysValidator(
            cast(
                Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
                into,
            ),
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
            field11,
            field12,
            field13,
            validate_object=validate_object,
        )

    elif field15 is None:
        return Dict14KeysValidator(
            cast(
                Callable[
                    [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            validate_object=validate_object,
        )

    elif field16 is None:
        return Dict15KeysValidator(
            cast(
                Callable[
                    [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15],
                    Ret,
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            field15,
            validate_object=validate_object,
        )

    elif field17 is None:
        return Dict16KeysValidator(
            cast(
                Callable[
                    [
                        T1,
                        T2,
                        T3,
                        T4,
                        T5,
                        T6,
                        T7,
                        T8,
                        T9,
                        T10,
                        T11,
                        T12,
                        T13,
                        T14,
                        T15,
                        T16,
                    ],
                    Ret,
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            validate_object=validate_object,
        )

    elif field18 is None:
        return Dict17KeysValidator(
            cast(
                Callable[
                    [
                        T1,
                        T2,
                        T3,
                        T4,
                        T5,
                        T6,
                        T7,
                        T8,
                        T9,
                        T10,
                        T11,
                        T12,
                        T13,
                        T14,
                        T15,
                        T16,
                        T17,
                    ],
                    Ret,
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            validate_object=validate_object,
        )

    elif field19 is None:
        return Dict18KeysValidator(
            cast(
                Callable[
                    [
                        T1,
                        T2,
                        T3,
                        T4,
                        T5,
                        T6,
                        T7,
                        T8,
                        T9,
                        T10,
                        T11,
                        T12,
                        T13,
                        T14,
                        T15,
                        T16,
                        T17,
                        T18,
                    ],
                    Ret,
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            field18,
            validate_object=validate_object,
        )

    elif field20 is None:
        return Dict19KeysValidator(
            cast(
                Callable[
                    [
                        T1,
                        T2,
                        T3,
                        T4,
                        T5,
                        T6,
                        T7,
                        T8,
                        T9,
                        T10,
                        T11,
                        T12,
                        T13,
                        T14,
                        T15,
                        T16,
                        T17,
                        T18,
                        T19,
                    ],
                    Ret,
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            field18,
            field19,
            validate_object=validate_object,
        )

    else:
        return Dict20KeysValidator(
            cast(
                Callable[
                    [
                        T1,
                        T2,
                        T3,
                        T4,
                        T5,
                        T6,
                        T7,
                        T8,
                        T9,
                        T10,
                        T11,
                        T12,
                        T13,
                        T14,
                        T15,
                        T16,
                        T17,
                        T18,
                        T19,
                        T20,
                    ],
                    Ret,
                ],
                into,
            ),
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
            field11,
            field12,
            field13,
            field14,
            field15,
            field16,
            field17,
            field18,
            field19,
            field20,
            validate_object=validate_object,
        )
