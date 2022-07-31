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
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
T10 = TypeVar("T10")
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


def _validate2_helper(
    state: Result[Callable[[T1, T2], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2], Ret], tuple[FailT, ...]] = Err(
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


def _validate3_helper(
    state: Result[Callable[[T1, T2, T3], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2, T3], Ret], tuple[FailT, ...]] = Err(
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


def _validate4_helper(
    state: Result[Callable[[T1, T2, T3, T4], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2, T3, T4], Ret], tuple[FailT, ...]] = Err(
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
        self.dv_field_lines = (
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
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
                self.dv_field_lines[4][0],
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
                _validate_with_key(self.dv_field_lines[4], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


def _validate5_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2, T3, T4, T5], Ret], tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate4_helper(next_state, r2, r3, r4, r5)


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
        self.dv_field_lines = (
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
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
                self.dv_field_lines[4][0],
                self.dv_field_lines[5][0],
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
                _validate_with_key(self.dv_field_lines[4], result.val),
                _validate_with_key(self.dv_field_lines[5], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


def _validate6_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6], Ret], tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate5_helper(next_state, r2, r3, r4, r5, r6)


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
        self.dv_field_lines = (
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
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
                self.dv_field_lines[4][0],
                self.dv_field_lines[5][0],
                self.dv_field_lines[6][0],
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
                _validate_with_key(self.dv_field_lines[4], result.val),
                _validate_with_key(self.dv_field_lines[5], result.val),
                _validate_with_key(self.dv_field_lines[6], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


def _validate7_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6, T7], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7], Ret], tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate6_helper(next_state, r2, r3, r4, r5, r6, r7)


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
        self.dv_field_lines = (
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
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
                self.dv_field_lines[4][0],
                self.dv_field_lines[5][0],
                self.dv_field_lines[6][0],
                self.dv_field_lines[7][0],
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
                _validate_with_key(self.dv_field_lines[4], result.val),
                _validate_with_key(self.dv_field_lines[5], result.val),
                _validate_with_key(self.dv_field_lines[6], result.val),
                _validate_with_key(self.dv_field_lines[7], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


def _validate8_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8], Ret], tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate7_helper(next_state, r2, r3, r4, r5, r6, r7, r8)


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
        self.dv_field_lines = (
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
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
                self.dv_field_lines[4][0],
                self.dv_field_lines[5][0],
                self.dv_field_lines[6][0],
                self.dv_field_lines[7][0],
                self.dv_field_lines[8][0],
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
                _validate_with_key(self.dv_field_lines[4], result.val),
                _validate_with_key(self.dv_field_lines[5], result.val),
                _validate_with_key(self.dv_field_lines[6], result.val),
                _validate_with_key(self.dv_field_lines[7], result.val),
                _validate_with_key(self.dv_field_lines[8], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


def _validate9_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret], tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
    r9: Result[T9, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9], Ret], tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate8_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9)


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
        self.dv_field_lines = (
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
                self.dv_field_lines[0][0],
                self.dv_field_lines[1][0],
                self.dv_field_lines[2][0],
                self.dv_field_lines[3][0],
                self.dv_field_lines[4][0],
                self.dv_field_lines[5][0],
                self.dv_field_lines[6][0],
                self.dv_field_lines[7][0],
                self.dv_field_lines[8][0],
                self.dv_field_lines[9][0],
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
                _validate_with_key(self.dv_field_lines[4], result.val),
                _validate_with_key(self.dv_field_lines[5], result.val),
                _validate_with_key(self.dv_field_lines[6], result.val),
                _validate_with_key(self.dv_field_lines[7], result.val),
                _validate_with_key(self.dv_field_lines[8], result.val),
                _validate_with_key(self.dv_field_lines[9], result.val),
            )
            return _flat_map_same_type_if_not_none(
                self.validate_object, result_1.map_err(_tuples_to_json_dict)
            )


def _validate10_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret], tuple[FailT, ...]
    ],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
    r9: Result[T9, FailT],
    r10: Result[T10, FailT],
) -> Result[Ret, tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret], tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate9_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10)


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
def _dict_validator(
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
def _dict_validator(
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
def _dict_validator(
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
def _dict_validator(
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
def _dict_validator(
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
def _dict_validator(
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


def _dict_validator(
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
    ],
    field1: KeyValidator[T1],
    field2: Optional[KeyValidator[T2]],
    field3: Optional[KeyValidator[T3]],
    field4: Optional[KeyValidator[T4]],
    field5: Optional[KeyValidator[T5]],
    field6: Optional[KeyValidator[T6]],
    field7: Optional[KeyValidator[T7]],
    field8: Optional[KeyValidator[T8]],
    field9: Optional[KeyValidator[T9]],
    field10: Optional[KeyValidator[T10]],
    *,
    validate_object: Callable[[Ret], Result[Ret, JSONValue]],
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

    else:
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


@overload
def validate_and_map(
    into: Callable[[T1], Ret],
    r1: Result[T1, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


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


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
    r9: Result[T9, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
    r9: Result[T9, FailT],
    r10: Result[T10, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, tuple[FailT, ...]]:
    ...


def validate_and_map(
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
    ],
    r1: Result[T1, FailT],
    r2: Optional[Result[T2, FailT]],
    r3: Optional[Result[T3, FailT]],
    r4: Optional[Result[T4, FailT]],
    r5: Optional[Result[T5, FailT]],
    r6: Optional[Result[T6, FailT]],
    r7: Optional[Result[T7, FailT]],
    r8: Optional[Result[T8, FailT]],
    r9: Optional[Result[T9, FailT]],
    r10: Optional[Result[T10, FailT]],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, tuple[FailT, ...]]]] = None,
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

    elif r5 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate4_helper(
                Ok(cast(Callable[[T1, T2, T3, T4], Ret], into)), r1, r2, r3, r4
            ),
        )

    elif r6 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate5_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5], Ret], into)), r1, r2, r3, r4, r5
            ),
        )

    elif r7 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate6_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5, T6], Ret], into)),
                r1,
                r2,
                r3,
                r4,
                r5,
                r6,
            ),
        )

    elif r8 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate7_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5, T6, T7], Ret], into)),
                r1,
                r2,
                r3,
                r4,
                r5,
                r6,
                r7,
            ),
        )

    elif r9 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate8_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret], into)),
                r1,
                r2,
                r3,
                r4,
                r5,
                r6,
                r7,
                r8,
            ),
        )

    elif r10 is None:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate9_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret], into)),
                r1,
                r2,
                r3,
                r4,
                r5,
                r6,
                r7,
                r8,
                r9,
            ),
        )

    else:

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate10_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret], into)),
                r1,
                r2,
                r3,
                r4,
                r5,
                r6,
                r7,
                r8,
                r9,
                r10,
            ),
        )
