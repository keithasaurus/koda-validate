"""Deprecated. Should be removed soon"""

from functools import partial
from typing import Callable, Optional, Tuple, Union, cast, overload

from koda_validate._generics import T1, T2, T3, FailT, Ret
from koda_validate._internals import _flat_map_same_type_if_not_none
from koda_validate.validated import Invalid, Valid, Validated


def _validate1_helper(
    state: Validated[Callable[[T1], Ret], Tuple[FailT, ...]], r: Validated[T1, FailT]
) -> Validated[Ret, Tuple[FailT, ...]]:
    if isinstance(r, Invalid):
        if isinstance(state, Invalid):
            return Invalid(state.val + (r.val,))
        else:
            return Invalid((r.val,))
    else:
        if isinstance(state, Invalid):
            return state
        else:
            return Valid(state.val(r.val))


def _validate2_helper(
    state: Validated[Callable[[T1, T2], Ret], Tuple[FailT, ...]],
    r1: Validated[T1, FailT],
    r2: Validated[T2, FailT],
) -> Validated[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Invalid):
        if isinstance(state, Invalid):
            next_state: Validated[Callable[[T2], Ret], Tuple[FailT, ...]] = Invalid(
                state.val + (r1.val,)
            )
        else:
            next_state = Invalid((r1.val,))
    else:
        if isinstance(state, Invalid):
            next_state = state
        else:
            next_state = Valid(partial(state.val, r1.val))

    return _validate1_helper(next_state, r2)


def _validate3_helper(
    state: Validated[Callable[[T1, T2, T3], Ret], Tuple[FailT, ...]],
    r1: Validated[T1, FailT],
    r2: Validated[T2, FailT],
    r3: Validated[T3, FailT],
) -> Validated[Ret, Tuple[FailT, ...]]:
    if isinstance(r1, Invalid):
        if isinstance(state, Invalid):
            next_state: Validated[Callable[[T2, T3], Ret], Tuple[FailT, ...]] = Invalid(
                state.val + (r1.val,)
            )
        else:
            next_state = Invalid((r1.val,))
    else:
        if isinstance(state, Invalid):
            next_state = state
        else:
            next_state = Valid(partial(state.val, r1.val))

    return _validate2_helper(next_state, r2, r3)


def _tupled(a: T1) -> Tuple[T1, ...]:
    return (a,)


def tupled_err_func(
    validate_object: Optional[Callable[[Ret], Validated[Ret, FailT]]]
) -> Callable[[Ret], Validated[Ret, Tuple[FailT, ...]]]:
    def inner(obj: Ret) -> Validated[Ret, Tuple[FailT, ...]]:
        if validate_object is None:
            return Valid(obj)
        else:
            return validate_object(obj).map_err(_tupled)

    return inner


@overload
def validate_and_map(
    into: Callable[[T1], Ret],
    r1: Validated[T1, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Validated[Ret, FailT]]] = None,
) -> Validated[Ret, Tuple[FailT, ...]]:
    ...  # pragma: no cover


@overload
def validate_and_map(
    into: Callable[[T1, T2], Ret],
    r1: Validated[T1, FailT],
    r2: Validated[T2, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Validated[Ret, FailT]]] = None,
) -> Validated[Ret, Tuple[FailT, ...]]:
    ...  # pragma: no cover


@overload
def validate_and_map(
    into: Callable[[T1, T2, T3], Ret],
    r1: Validated[T1, FailT],
    r2: Validated[T2, FailT],
    r3: Validated[T3, FailT],
    *,
    validate_object: Optional[Callable[[Ret], Validated[Ret, FailT]]] = None,
) -> Validated[Ret, Tuple[FailT, ...]]:
    ...  # pragma: no cover


def validate_and_map(
    into: Union[
        Callable[[T1], Ret],
        Callable[[T1, T2], Ret],
        Callable[[T1, T2, T3], Ret],
    ],
    r1: Validated[T1, FailT],
    r2: Optional[Validated[T2, FailT]] = None,
    r3: Optional[Validated[T3, FailT]] = None,
    *,
    validate_object: Optional[Callable[[Ret], Validated[Ret, FailT]]] = None,
) -> Validated[Ret, Tuple[FailT, ...]]:
    if r2 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate1_helper(Valid(cast(Callable[[T1], Ret], into)), r1),
        )
    elif r3 is None:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate2_helper(Valid(cast(Callable[[T1, T2], Ret], into)), r1, r2),
        )

    else:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate3_helper(Valid(cast(Callable[[T1, T2, T3], Ret], into)), r1, r2, r3),
        )
