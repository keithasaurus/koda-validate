from typing import Any, Callable, Final, Generic, Optional, TypeVar, Union, cast, overload

from koda import Err, Maybe, Ok, Result, mapping_get

from koda_validate.typedefs import JSONValue, Predicate, Validator, ValidatorFunc
from koda_validate.utils import expected
from koda_validate.validators.utils import _flat_map_same_type_if_not_none
from koda_validate.validators.validate_and_map import validate_and_map

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
T21 = TypeVar("T21")
T22 = TypeVar("T22")
T23 = TypeVar("T23")
T24 = TypeVar("T24")
T25 = TypeVar("T25")
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


OBJECT_ERRORS_FIELD: Final[str] = "__object__"


class MapValidator(Validator[Any, dict[T1, T2], JSONValue]):
    """Note that while a key should always be expected to be received as a string,
    it's possible that we may want to validate and cast it to a different
    type (i.e. a date)
    """

    def __init__(
        self,
        key_validator: Validator[Any, T1, JSONValue],
        value_validator: Validator[Any, T2, JSONValue],
        *dict_validators: Predicate[dict[T1, T2], JSONValue],
    ) -> None:
        self.key_validator = key_validator
        self.value_validator = value_validator
        self.dict_validators = dict_validators

    def __call__(self, data: Any) -> Result[dict[T1, T2], JSONValue]:
        if isinstance(data, dict):
            return_dict: dict[T1, T2] = {}
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


class IsDict(Validator[Any, dict[Any, Any], JSONValue]):
    def __call__(self, val: Any) -> Result[dict[Any, Any], JSONValue]:
        if isinstance(val, dict):
            return Ok(val)
        else:
            return Err({OBJECT_ERRORS_FIELD: [expected("an object")]})


def _has_no_extra_keys(
    keys: set[str],
) -> ValidatorFunc[dict[T1, T2], dict[T1, T2], JSONValue]:
    def inner(mapping: dict[T1, T2]) -> Result[dict[T1, T2], JSONValue]:
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


def _dict_without_extra_keys(
    keys: set[str], data: Any
) -> Result[dict[Any, Any], JSONValue]:
    return IsDict()(data).flat_map(_has_no_extra_keys(keys))


def _tuples_to_json_dict(data: tuple[tuple[str, JSONValue], ...]) -> JSONValue:
    return dict(data)


KeyValidator = tuple[str, Callable[[Maybe[Any]], Result[T1, JSONValue]]]


def _validate_with_key(
    r: KeyValidator[T1], data: dict[Any, Any]
) -> Result[T1, tuple[str, JSONValue]]:
    key, fn = r

    def add_key(val: JSONValue) -> tuple[str, JSONValue]:
        return key, val

    return fn(mapping_get(data, key)).map_err(add_key)


class Dict1KeysValidator(Generic[T1, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        into: Callable[[T1], Ret],
        field1: KeyValidator[T1],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (field1,)
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys({self.dv_fields[0][0]}, data)

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict2KeysValidator(Generic[T1, T2, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        into: Callable[[T1, T2], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {self.dv_fields[0][0], self.dv_fields[1][0]}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict3KeysValidator(Generic[T1, T2, T3, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        into: Callable[[T1, T2, T3], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {self.dv_fields[0][0], self.dv_fields[1][0], self.dv_fields[2][0]}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict4KeysValidator(Generic[T1, T2, T3, T4, Ret], Validator[Any, Ret, JSONValue]):
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
    ) -> None:
        self.into = into
        self.dv_fields = (
            field1,
            field2,
            field3,
            field4,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict5KeysValidator(
    Generic[T1, T2, T3, T4, T5, Ret], Validator[Any, Ret, JSONValue]
):
    def __init__(
        self,
        into: Callable[[T1, T2, T3, T4, T5], Ret],
        field1: KeyValidator[T1],
        field2: KeyValidator[T2],
        field3: KeyValidator[T3],
        field4: KeyValidator[T4],
        field5: KeyValidator[T5],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict6KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, Ret], Validator[Any, Ret, JSONValue]
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict7KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, Ret], Validator[Any, Ret, JSONValue]
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict8KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, Ret], Validator[Any, Ret, JSONValue]
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict9KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, Ret], Validator[Any, Ret, JSONValue]
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict10KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, Ret], Validator[Any, Ret, JSONValue]
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict11KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, Ret],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict12KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, Ret],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict13KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, Ret],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict14KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, Ret],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict15KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, Ret],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict16KeysValidator(
    Generic[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, Ret],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict17KeysValidator(
    Generic[
        T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, Ret
    ],
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
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
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
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
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
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
    Validator[Any, Ret, JSONValue],
):
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
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
                self.dv_fields[19][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
                _validate_with_key(self.dv_fields[19], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict21KeysValidator(
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
        T21,
        Ret,
    ],
    Validator[Any, Ret, JSONValue],
):
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
                T21,
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
        field21: KeyValidator[T21],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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
            field21,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
                self.dv_fields[19][0],
                self.dv_fields[20][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
                _validate_with_key(self.dv_fields[19], result.val),
                _validate_with_key(self.dv_fields[20], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict22KeysValidator(
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
        T21,
        T22,
        Ret,
    ],
    Validator[Any, Ret, JSONValue],
):
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
                T21,
                T22,
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
        field21: KeyValidator[T21],
        field22: KeyValidator[T22],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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
            field21,
            field22,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
                self.dv_fields[19][0],
                self.dv_fields[20][0],
                self.dv_fields[21][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
                _validate_with_key(self.dv_fields[19], result.val),
                _validate_with_key(self.dv_fields[20], result.val),
                _validate_with_key(self.dv_fields[21], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict23KeysValidator(
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
        T21,
        T22,
        T23,
        Ret,
    ],
    Validator[Any, Ret, JSONValue],
):
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
                T21,
                T22,
                T23,
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
        field21: KeyValidator[T21],
        field22: KeyValidator[T22],
        field23: KeyValidator[T23],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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
            field21,
            field22,
            field23,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
                self.dv_fields[19][0],
                self.dv_fields[20][0],
                self.dv_fields[21][0],
                self.dv_fields[22][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
                _validate_with_key(self.dv_fields[19], result.val),
                _validate_with_key(self.dv_fields[20], result.val),
                _validate_with_key(self.dv_fields[21], result.val),
                _validate_with_key(self.dv_fields[22], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict24KeysValidator(
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
        T21,
        T22,
        T23,
        T24,
        Ret,
    ],
    Validator[Any, Ret, JSONValue],
):
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
                T21,
                T22,
                T23,
                T24,
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
        field21: KeyValidator[T21],
        field22: KeyValidator[T22],
        field23: KeyValidator[T23],
        field24: KeyValidator[T24],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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
            field21,
            field22,
            field23,
            field24,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
                self.dv_fields[19][0],
                self.dv_fields[20][0],
                self.dv_fields[21][0],
                self.dv_fields[22][0],
                self.dv_fields[23][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
                _validate_with_key(self.dv_fields[19], result.val),
                _validate_with_key(self.dv_fields[20], result.val),
                _validate_with_key(self.dv_fields[21], result.val),
                _validate_with_key(self.dv_fields[22], result.val),
                _validate_with_key(self.dv_fields[23], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


class Dict25KeysValidator(
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
        T21,
        T22,
        T23,
        T24,
        T25,
        Ret,
    ],
    Validator[Any, Ret, JSONValue],
):
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
                T21,
                T22,
                T23,
                T24,
                T25,
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
        field21: KeyValidator[T21],
        field22: KeyValidator[T22],
        field23: KeyValidator[T23],
        field24: KeyValidator[T24],
        field25: KeyValidator[T25],
        *,
        validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
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
            field21,
            field22,
            field23,
            field24,
            field25,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_fields[0][0],
                self.dv_fields[1][0],
                self.dv_fields[2][0],
                self.dv_fields[3][0],
                self.dv_fields[4][0],
                self.dv_fields[5][0],
                self.dv_fields[6][0],
                self.dv_fields[7][0],
                self.dv_fields[8][0],
                self.dv_fields[9][0],
                self.dv_fields[10][0],
                self.dv_fields[11][0],
                self.dv_fields[12][0],
                self.dv_fields[13][0],
                self.dv_fields[14][0],
                self.dv_fields[15][0],
                self.dv_fields[16][0],
                self.dv_fields[17][0],
                self.dv_fields[18][0],
                self.dv_fields[19][0],
                self.dv_fields[20][0],
                self.dv_fields[21][0],
                self.dv_fields[22][0],
                self.dv_fields[23][0],
                self.dv_fields[24][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_fields[0], result.val),
                _validate_with_key(self.dv_fields[1], result.val),
                _validate_with_key(self.dv_fields[2], result.val),
                _validate_with_key(self.dv_fields[3], result.val),
                _validate_with_key(self.dv_fields[4], result.val),
                _validate_with_key(self.dv_fields[5], result.val),
                _validate_with_key(self.dv_fields[6], result.val),
                _validate_with_key(self.dv_fields[7], result.val),
                _validate_with_key(self.dv_fields[8], result.val),
                _validate_with_key(self.dv_fields[9], result.val),
                _validate_with_key(self.dv_fields[10], result.val),
                _validate_with_key(self.dv_fields[11], result.val),
                _validate_with_key(self.dv_fields[12], result.val),
                _validate_with_key(self.dv_fields[13], result.val),
                _validate_with_key(self.dv_fields[14], result.val),
                _validate_with_key(self.dv_fields[15], result.val),
                _validate_with_key(self.dv_fields[16], result.val),
                _validate_with_key(self.dv_fields[17], result.val),
                _validate_with_key(self.dv_fields[18], result.val),
                _validate_with_key(self.dv_fields[19], result.val),
                _validate_with_key(self.dv_fields[20], result.val),
                _validate_with_key(self.dv_fields[21], result.val),
                _validate_with_key(self.dv_fields[22], result.val),
                _validate_with_key(self.dv_fields[23], result.val),
                _validate_with_key(self.dv_fields[24], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


@overload
def dict_validator(
    into: Callable[[T1], Ret],
    field1: KeyValidator[T1],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...


@overload
def dict_validator(
    into: Callable[[T1, T2, T3, T4], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    field4: KeyValidator[T4],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
            T21,
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
    field21: KeyValidator[T21],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
            T21,
            T22,
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
    field21: KeyValidator[T21],
    field22: KeyValidator[T22],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
            T21,
            T22,
            T23,
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
    field21: KeyValidator[T21],
    field22: KeyValidator[T22],
    field23: KeyValidator[T23],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
            T21,
            T22,
            T23,
            T24,
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
    field21: KeyValidator[T21],
    field22: KeyValidator[T22],
    field23: KeyValidator[T23],
    field24: KeyValidator[T24],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
            T21,
            T22,
            T23,
            T24,
            T25,
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
    field21: KeyValidator[T21],
    field22: KeyValidator[T22],
    field23: KeyValidator[T23],
    field24: KeyValidator[T24],
    field25: KeyValidator[T25],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
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
                T21,
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
                T21,
                T22,
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
                T21,
                T22,
                T23,
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
                T21,
                T22,
                T23,
                T24,
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
                T21,
                T22,
                T23,
                T24,
                T25,
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
    field21: Optional[KeyValidator[T21]] = None,
    field22: Optional[KeyValidator[T22]] = None,
    field23: Optional[KeyValidator[T23]] = None,
    field24: Optional[KeyValidator[T24]] = None,
    field25: Optional[KeyValidator[T25]] = None,
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:

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

    elif field21 is None:
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

    elif field22 is None:
        return Dict21KeysValidator(
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
                        T21,
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
            field21,
            validate_object=validate_object,
        )

    elif field23 is None:
        return Dict22KeysValidator(
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
                        T21,
                        T22,
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
            field21,
            field22,
            validate_object=validate_object,
        )

    elif field24 is None:
        return Dict23KeysValidator(
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
                        T21,
                        T22,
                        T23,
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
            field21,
            field22,
            field23,
            validate_object=validate_object,
        )

    elif field25 is None:
        return Dict24KeysValidator(
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
                        T21,
                        T22,
                        T23,
                        T24,
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
            field21,
            field22,
            field23,
            field24,
            validate_object=validate_object,
        )

    else:
        return Dict25KeysValidator(
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
                        T21,
                        T22,
                        T23,
                        T24,
                        T25,
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
            field21,
            field22,
            field23,
            field24,
            field25,
            validate_object=validate_object,
        )
