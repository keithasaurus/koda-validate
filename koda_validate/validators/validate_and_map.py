from functools import partial
from typing import Callable, Optional, Tuple, TypeVar, Union, cast, overload

from koda import Err, Ok, Result

from koda_validate.validators.utils import _flat_map_same_type_if_not_none

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


def _validate13_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
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
    r13: Result[T13, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate12_helper(
        next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13
    )


def _validate14_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret],
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret],
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate13_helper(
        next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14
    )


def _validate15_helper(
    state: Result[
        Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret],
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[
                    [T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret
                ],
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate14_helper(
        next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15
    )


def _validate16_helper(
    state: Result[
        Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16], Ret
        ],
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[
                    [T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16],
                    Ret,
                ],
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate15_helper(
        next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16
    )


def _validate17_helper(
    state: Result[
        Callable[
            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17],
            Ret,
        ],
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[
                    [
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
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate16_helper(
        next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17
    )


def _validate18_helper(
    state: Result[
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    r18: Result[T18, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[
                    [
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
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate17_helper(
        next_state,
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
        r13,
        r14,
        r15,
        r16,
        r17,
        r18,
    )


def _validate19_helper(
    state: Result[
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    r18: Result[T18, FailT],
    r19: Result[T19, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[
                    [
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
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate18_helper(
        next_state,
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
        r13,
        r14,
        r15,
        r16,
        r17,
        r18,
        r19,
    )


def _validate20_helper(
    state: Result[
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    r18: Result[T18, FailT],
    r19: Result[T19, FailT],
    r20: Result[T20, FailT],
) -> Result[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[
                    [
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
                Tuple[FailT, ...],
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate19_helper(
        next_state,
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
        r13,
        r14,
        r15,
        r16,
        r17,
        r18,
        r19,
        r20,
    )


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


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret],
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
    r13: Result[T13, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14], Ret],
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15], Ret
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16], Ret
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17], Ret
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
    into: Callable[
        [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18],
        Ret,
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    r18: Result[T18, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    r18: Result[T18, FailT],
    r19: Result[T19, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def validate_and_map(
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
    r13: Result[T13, FailT],
    r14: Result[T14, FailT],
    r15: Result[T15, FailT],
    r16: Result[T16, FailT],
    r17: Result[T17, FailT],
    r18: Result[T18, FailT],
    r19: Result[T19, FailT],
    r20: Result[T20, FailT],
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
    r13: Optional[Result[T13, FailT]] = None,
    r14: Optional[Result[T14, FailT]] = None,
    r15: Optional[Result[T15, FailT]] = None,
    r16: Optional[Result[T16, FailT]] = None,
    r17: Optional[Result[T17, FailT]] = None,
    r18: Optional[Result[T18, FailT]] = None,
    r19: Optional[Result[T19, FailT]] = None,
    r20: Optional[Result[T20, FailT]] = None,
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

    elif r13 is None:

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

    elif r14 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate13_helper(
                Ok(
                    cast(
                        Callable[
                            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13], Ret
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
                r13,
            ),
        )

    elif r15 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate14_helper(
                Ok(
                    cast(
                        Callable[
                            [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14],
                            Ret,
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
                r13,
                r14,
            ),
        )

    elif r16 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate15_helper(
                Ok(
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
                            ],
                            Ret,
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
                r13,
                r14,
                r15,
            ),
        )

    elif r17 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate16_helper(
                Ok(
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
                r13,
                r14,
                r15,
                r16,
            ),
        )

    elif r18 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate17_helper(
                Ok(
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
                r13,
                r14,
                r15,
                r16,
                r17,
            ),
        )

    elif r19 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate18_helper(
                Ok(
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
                r13,
                r14,
                r15,
                r16,
                r17,
                r18,
            ),
        )

    elif r20 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate19_helper(
                Ok(
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
                r13,
                r14,
                r15,
                r16,
                r17,
                r18,
                r19,
            ),
        )

    else:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate20_helper(
                Ok(
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
                r13,
                r14,
                r15,
                r16,
                r17,
                r18,
                r19,
                r20,
            ),
        )
