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


def validate_and_map(
    into: Union[
        Callable[[T1], Ret],
        Callable[[T1, T2], Ret],
        Callable[[T1, T2, T3], Ret],
    ],
    r1: Result[T1, FailT],
    r2: Optional[Result[T2, FailT]] = None,
    r3: Optional[Result[T3, FailT]] = None,
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

    else:

        return _flat_map_same_type_if_not_none(
            tupled_err_func(validate_object),
            _validate3_helper(Ok(cast(Callable[[T1, T2, T3], Ret], into)), r1, r2, r3),
        )
