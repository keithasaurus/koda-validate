from functools import partial
from typing import Callable, Optional, Tuple, TypeVar, Union, cast, overload

from koda import Err, Ok, Result

from koda_validate.utils import _flat_map_same_type_if_not_none

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
Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


def _validate1_helper(
    state: Result[Callable[[T1], Ret], Tuple[FailT, ...]], r: Result[T1, FailT]
) -> Result[Ret, Tuple[FailT, ...]]:
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


def _validate2_helper(
    state: Result[Callable[[T1, T2], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2], Ret], Tuple[FailT, ...]] = Err(
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


def _validate3_helper(
    state: Result[Callable[[T1, T2, T3], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2, T3], Ret], Tuple[FailT, ...]] = Err(
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


def _validate4_helper(
    state: Result[Callable[[T1, T2, T3, T4], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2, T3, T4], Ret], Tuple[FailT, ...]] = Err(
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


def _validate5_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[T2, T3, T4, T5], Ret], Tuple[FailT, ...]] = Err(
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


def _validate6_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6], Ret], Tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate5_helper(next_state, r2, r3, r4, r5, r6)


def _validate7_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6, T7], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7], Ret], Tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate6_helper(next_state, r2, r3, r4, r5, r6, r7)


def _validate8_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6, T7, T8], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8], Ret], Tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate7_helper(next_state, r2, r3, r4, r5, r6, r7, r8)


def _validate9_helper(
    state: Result[Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], Ret], Tuple[FailT, ...]],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    r4: Result[T4, FailT],
    r5: Result[T5, FailT],
    r6: Result[T6, FailT],
    r7: Result[T7, FailT],
    r8: Result[T8, FailT],
    r9: Result[T9, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9], Ret], Tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate8_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9)


def _validate10_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret], Tuple[FailT, ...]
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
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9, T10], Ret], Tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate9_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10)


def _validate11_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret], Tuple[FailT, ...]
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
    r11: Result[T11, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate10_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11)


def _validate12_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
        Tuple[FailT, ...],
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
    r11: Result[T11, FailT],
    r12: Result[T12, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate11_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12)


def _tupled(a: T1) -> Tuple[T1, ...]:
    return (a,)


def tupled_err_func(
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]]
) -> Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]:
    def inner(obj: Ret) -> Result[Ret, Tuple[FailT, ...]]:
        if validate_object is None:
            return Ok(obj)
        else:
            return validate_object(obj).map_err(_tupled)

    return inner


@overload
def validate_and_map(
    into: Callable[[T1], Ret],
    r1: Result[T1, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3], Ret],
    r1: Result[T1, FailT],
    r2: Result[T2, FailT],
    r3: Result[T3, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
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
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
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
    r11: Result[T11, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
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
    r11: Result[T11, FailT],
    r12: Result[T12, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
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
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret],
    ],
    r1: Result[T1, FailT],
    r2: Optional[Result[T2, FailT]] = None,
    r3: Optional[Result[T3, FailT]] = None,
    r4: Optional[Result[T4, FailT]] = None,
    r5: Optional[Result[T5, FailT]] = None,
    r6: Optional[Result[T6, FailT]] = None,
    r7: Optional[Result[T7, FailT]] = None,
    r8: Optional[Result[T8, FailT]] = None,
    r9: Optional[Result[T9, FailT]] = None,
    r10: Optional[Result[T10, FailT]] = None,
    r11: Optional[Result[T11, FailT]] = None,
    r12: Optional[Result[T12, FailT]] = None,
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:

    if r2 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate1_helper(Ok(cast(Callable[[T1], Ret], into)), r1),
        )
    elif r3 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate2_helper(Ok(cast(Callable[[T1, T2], Ret], into)), r1, r2),
        )

    elif r4 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate3_helper(Ok(cast(Callable[[T1, T2, T3], Ret], into)), r1, r2, r3),
        )

    elif r5 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate4_helper(
                Ok(cast(Callable[[T1, T2, T3, T4], Ret], into)), r1, r2, r3, r4
            ),
        )

    elif r6 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate5_helper(
                Ok(cast(Callable[[T1, T2, T3, T4, T5], Ret], into)), r1, r2, r3, r4, r5
            ),
        )

    elif r7 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
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
            tupled_err_func(validate_object),
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
            tupled_err_func(validate_object),
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
            tupled_err_func(validate_object),
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

    elif r11 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
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

    elif r12 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate11_helper(
                Ok(
                    cast(
                        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11], Ret],
                        into,
                    )
                ),
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
                r11,
            ),
        )

    else:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate12_helper(
                Ok(
                    cast(
                        Callable[
                            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12], Ret
                        ],
                        into,
                    )
                ),
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
                r11,
                r12,
            ),
        )
