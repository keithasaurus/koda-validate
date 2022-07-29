from functools import partial
from typing import Any, Callable, Generic, Optional, TypeVar, Union, cast, overload

from koda import Err, Maybe, Ok, Result, mapping_get

from koda_validate._cruft import _flat_map_same_type_if_not_none
from koda_validate.typedefs import JSONValue, Validator
from koda_validate.validators import _dict_without_extra_keys, _validate_with_key

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


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
        self.dv_field_lines = (field1,)
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys({self.dv_field_lines[0][0]}, data)

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_field_lines[0], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


@overload
def _dict_validator(
    into: Callable[[T1], Ret],
    field1: KeyValidator[T1],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...


@overload
def _dict_validator(
    into: Callable[[T1, T2], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...


@overload
def _dict_validator(
    into: Callable[[T1, T2, T3], Ret],
    field1: KeyValidator[T1],
    field2: KeyValidator[T2],
    field3: KeyValidator[T3],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, JSONValue]]] = None,
) -> Validator[Any, Ret, JSONValue]:
    ...


@overload
def _dict_validator(
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
def validate_and_map(
    into: Callable[[T1], Ret],
    r1: Result[T1, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


def _validate1_helper(
    state: Result[Callable[[T1], Ret], tuple[FailT, ...]], r: Result[T1, FailT]
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r, Err):
        if isinstance(state, Err):
            return Err(state.val + (r.val,))
        else:
            return Err((r.val,))
    else:
        if isinstance(state, Err):
            return state
        else:
            return Ok(state.val(r.val))


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
        self.dv_field_lines = (
            field1,
            field2,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {self.dv_field_lines[0][0], self.dv_field_lines[1][0]}, data
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_field_lines[0], result.val),
                _validate_with_key(self.dv_field_lines[1], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


@overload
def validate_and_map(
    into: Callable[[T1, T2], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


def _validate2_helper(
    state: Result[Callable[[T1, T2], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T1, T2], Ret], tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate1_helper(next_state, r2)


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
        self.dv_field_lines = (
            field1,
            field2,
            field3,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_field_lines[0], result.val),
                _validate_with_key(self.dv_field_lines[1], result.val),
                _validate_with_key(self.dv_field_lines[2], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


def _validate3_helper(
    state: Result[Callable[[T1, T2, T3], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T1, T2, T3], Ret], tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate2_helper(next_state, r2, r3)


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
        self.dv_field_lines = (
            field1,
            field2,
            field3,
            field4,
        )
        self.validate_object = validate_object

    def __call__(self, data: Any) -> Result[Ret, JSONValue]:
        result = _dict_without_extra_keys(
            {
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
            },
            data,
        )

        if isinstance(result, Err):
            return result
        else:
            result_1 = validate_and_map(
                self.into,
                _validate_with_key(self.dv_field_lines[0], result.val),
                _validate_with_key(self.dv_field_lines[1], result.val),
                _validate_with_key(self.dv_field_lines[2], result.val),
                _validate_with_key(self.dv_field_lines[3], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


def _validate4_helper(
    state: Result[Callable[[T1, T2, T3, T4], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T1, T2, T3, T4], Ret], tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate3_helper(next_state, r2, r3, r4)


def _dict_validator(
    into: Union[
        Callable[[T1], Ret],
        Callable[[T1, T2], Ret],
        Callable[[T1, T2, T3], Ret],
        Callable[[T1, T2, T3, T4], Ret],
    ],
    field1: KeyValidator[T1],
    field2: Optional[KeyValidator[T2]],
    field3: Optional[KeyValidator[T3]],
    field4: Optional[KeyValidator[T4]],
    *,
    validate_object: Callable[[Ret], Result[Ret, JSONValue]],
) -> Validator[Any, Ret, JSONValue]:

    if field2 is None:
        return Dict1KeysValidator(into, field1, validate_object=validate_object)
    elif field3 is None:
        return Dict2KeysValidator(into, field1, field2, validate_object=validate_object)

    elif field4 is None:
        return Dict3KeysValidator(
            into, field1, field2, field3, validate_object=validate_object
        )

    else:
        return Dict4KeysValidator(
            into, field1, field2, field3, field4, validate_object=validate_object
        )


def validate_and_map(
    into: Union[
        Callable[[T1], Ret],
        Callable[[T1, T2], Ret],
        Callable[[T1, T2, T3], Ret],
        Callable[[T1, T2, T3, T4], Ret],
    ],
    r1: Result[T1, FailT],
    r2: Optional[Result[T2, FailT]],
    r3: Optional[Result[T3, FailT]],
    r4: Optional[Result[T4, FailT]],
    *,
    validate_object: Callable[[Ret], Result[Ret, JSONValue]],
) -> Result[Ret, tuple[FailT, ...]]:

    if r2 is None:

        return _flat_map_same_type_if_not_none(
            validate_object, _validate1_helper(Ok(cast(Callable[[T1], Ret], into)), r1)
        )
    elif r3 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate2_helper(Ok(cast(Callable[[T1, T2], Ret], into)), r1, r2),
        )

    elif r4 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate3_helper(Ok(cast(Callable[[T1, T2, T3], Ret], into)), r1, r2, r3),
        )

    else:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate4_helper(
                Ok(cast(Callable[[T1, T2, T3, T4], Ret], into)), r1, r2, r3, r4
            ),
        )
