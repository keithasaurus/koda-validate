from __future__ import annotations

from functools import partial
from typing import Callable, Optional, Tuple, Union, overload

from koda.result import Err, Ok, Result

from koda_validate._generics import A, B, C, D, E, F, FailT, G, H, I, J, K, Ret

# simple alias allows to greatly reduce amount of characters required to define
# validators
_Validator = Callable[[A], Result[B, FailT]]


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Result[A, FailT]]],
    r: Result[A, FailT],
) -> Result[A, FailT]:
    if fn is None:
        return r
    else:
        return r.flat_map(fn)


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Callable[[A], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Callable[[A, B], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Callable[[A, B, C], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Callable[[A, B, C, D], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Callable[[A, B, C, D, E], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Callable[[A, B, C, D, E, F], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Callable[[A, B, C, D, E, F, G], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Result[H, FailT],
    r9: Callable[[A, B, C, D, E, F, G, H], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Result[H, FailT],
    r9: Result[I, FailT],
    r10: Callable[[A, B, C, D, E, F, G, H, I], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


@overload
def _validate_and_map(
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Result[H, FailT],
    r9: Result[I, FailT],
    r10: Result[J, FailT],
    r11: Callable[[A, B, C, D, E, F, G, H, I, J], Ret],
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    ...


def _validate_and_map(
    r1: Result[A, FailT],
    r2: Callable[[A], Ret] | Result[B, FailT],
    r3: None | Callable[[A, B], Ret] | Result[C, FailT] = None,
    r4: None | Callable[[A, B, C], Ret] | Result[D, FailT] = None,
    r5: None | Callable[[A, B, C, D], Ret] | Result[E, FailT] = None,
    r6: None | Callable[[A, B, C, D, E], Ret] | Result[F, FailT] = None,
    r7: None | Callable[[A, B, C, D, E, F], Ret] | Result[G, FailT] = None,
    r8: None | Callable[[A, B, C, D, E, F, G], Ret] | Result[H, FailT] = None,
    r9: None | Callable[[A, B, C, D, E, F, G, H], Ret] | Result[I, FailT] = None,
    r10: None | Callable[[A, B, C, D, E, F, G, H, I], Ret] | Result[J, FailT] = None,
    r11: None | Callable[[A, B, C, D, E, F, G, H, I, J], Ret] = None,
    *,
    validate_object: Optional[Callable[[Ret], Result[Ret, Tuple[FailT, ...]]]] = None,
) -> Result[Ret, Tuple[FailT, ...]]:
    """
    See overloaded signatures above for better idea of what's happening here

    Note that the assertions below should already be guaranteed by mypy
    """
    if callable(r2):
        return _flat_map_same_type_if_not_none(
            validate_object, _validate1_helper(Ok(r2), r1)
        )
    elif callable(r3):
        return _flat_map_same_type_if_not_none(
            validate_object, _validate2_helper(Ok(r3), r1, r2)
        )
    elif callable(r4):
        assert r3 is not None
        return _flat_map_same_type_if_not_none(
            validate_object, _validate3_helper(Ok(r4), r1, r2, r3)
        )
    elif callable(r5):
        assert r3 is not None
        assert r4 is not None
        return _flat_map_same_type_if_not_none(
            validate_object, _validate4_helper(Ok(r5), r1, r2, r3, r4)
        )
    elif callable(r6):
        assert r3 is not None
        assert r4 is not None
        assert r5 is not None

        return _flat_map_same_type_if_not_none(
            validate_object, _validate5_helper(Ok(r6), r1, r2, r3, r4, r5)
        )
    elif callable(r7):
        assert r3 is not None
        assert r4 is not None
        assert r5 is not None
        assert r6 is not None

        return _flat_map_same_type_if_not_none(
            validate_object, _validate6_helper(Ok(r7), r1, r2, r3, r4, r5, r6)
        )
    elif callable(r8):
        assert r3 is not None
        assert r4 is not None
        assert r5 is not None
        assert r6 is not None
        assert r7 is not None

        return _flat_map_same_type_if_not_none(
            validate_object, _validate7_helper(Ok(r8), r1, r2, r3, r4, r5, r6, r7)
        )
    elif callable(r9):
        assert r3 is not None
        assert r4 is not None
        assert r5 is not None
        assert r6 is not None
        assert r7 is not None
        assert r8 is not None

        return _flat_map_same_type_if_not_none(
            validate_object, _validate8_helper(Ok(r9), r1, r2, r3, r4, r5, r6, r7, r8)
        )
    elif callable(r10):
        assert r3 is not None
        assert r4 is not None
        assert r5 is not None
        assert r6 is not None
        assert r7 is not None
        assert r8 is not None
        assert r9 is not None

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate9_helper(Ok(r10), r1, r2, r3, r4, r5, r6, r7, r8, r9),
        )
    else:
        assert r3 is not None
        assert r4 is not None
        assert r5 is not None
        assert r6 is not None
        assert r7 is not None
        assert r8 is not None
        assert r9 is not None
        assert r10 is not None
        assert callable(r11)

        return _flat_map_same_type_if_not_none(
            validate_object,
            _validate10_helper(Ok(r11), r1, r2, r3, r4, r5, r6, r7, r8, r9, r10),
        )


@overload
def _chain(
    fn1: _Validator[A, B, FailT], fn2: _Validator[B, C, FailT]
) -> _Validator[A, C, FailT]:
    ...


@overload
def _chain(
    fn1: _Validator[A, B, FailT],
    fn2: _Validator[B, C, FailT],
    fn3: _Validator[C, D, FailT],
) -> _Validator[A, D, FailT]:
    ...


@overload
def _chain(
    fn1: _Validator[A, B, FailT],
    fn2: _Validator[B, C, FailT],
    fn3: _Validator[C, D, FailT],
    fn4: _Validator[D, E, FailT],
) -> _Validator[A, E, FailT]:
    ...


@overload
def _chain(
    fn1: _Validator[A, B, FailT],
    fn2: _Validator[B, C, FailT],
    fn3: _Validator[C, D, FailT],
    fn4: _Validator[D, E, FailT],
    fn5: _Validator[E, F, FailT],
) -> _Validator[A, F, FailT]:
    ...


@overload
def _chain(
    fn1: _Validator[A, B, FailT],
    fn2: _Validator[B, C, FailT],
    fn3: _Validator[C, D, FailT],
    fn4: _Validator[D, E, FailT],
    fn5: _Validator[E, F, FailT],
    fn6: _Validator[F, G, FailT],
) -> _Validator[A, G, FailT]:
    ...


def _chain(
    fn1: _Validator[A, B, FailT],
    fn2: _Validator[B, C, FailT],
    fn3: Optional[_Validator[C, D, FailT]] = None,
    fn4: Optional[_Validator[D, E, FailT]] = None,
    fn5: Optional[_Validator[E, F, FailT]] = None,
    fn6: Optional[_Validator[F, G, FailT]] = None,
) -> Callable[
    [A],
    Union[
        Result[C, FailT],
        Result[D, FailT],
        Result[E, FailT],
        Result[F, FailT],
        Result[G, FailT],
    ],
]:
    def inner(
        val: A,
    ) -> Union[
        Result[C, FailT],
        Result[D, FailT],
        Result[E, FailT],
        Result[F, FailT],
        Result[G, FailT],
    ]:
        if fn3 is None:
            return fn1(val).flat_map(fn2)
        elif fn4 is None:
            return fn1(val).flat_map(fn2).flat_map(fn3)
        elif fn5 is None:
            return fn1(val).flat_map(fn2).flat_map(fn3).flat_map(fn4)
        elif fn6 is None:
            return fn1(val).flat_map(fn2).flat_map(fn3).flat_map(fn4).flat_map(fn5)
        else:
            return (
                fn1(val)
                .flat_map(fn2)
                .flat_map(fn3)
                .flat_map(fn4)
                .flat_map(fn5)
                .flat_map(fn6)
            )

    return inner


def _validate1_helper(
    state: Result[Callable[[A], B], Tuple[FailT, ...]], r: Result[A, FailT]
) -> Result[B, Tuple[FailT, ...]]:
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
    state: Result[Callable[[A, B], C], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
) -> Result[C, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[B], C], Tuple[FailT, ...]] = Err(
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
    state: Result[Callable[[A, B, C], D], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
) -> Result[D, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[B, C], D], Tuple[FailT, ...]] = Err(
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
    state: Result[Callable[[A, B, C, D], E], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
) -> Result[E, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[B, C, D], E], Tuple[FailT, ...]] = Err(
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
    state: Result[Callable[[A, B, C, D, E], F], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
) -> Result[F, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[B, C, D, E], F], Tuple[FailT, ...]] = Err(
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
    state: Result[Callable[[A, B, C, D, E, F], G], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
) -> Result[G, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[B, C, D, E, F], G], Tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate5_helper(next_state, r2, r3, r4, r5, r6)


def _validate7_helper(
    state: Result[Callable[[A, B, C, D, E, F, G], H], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
) -> Result[H, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[Callable[[B, C, D, E, F, G], H], Tuple[FailT, ...]] = Err(
                state.val + (r1.val,)
            )
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate6_helper(next_state, r2, r3, r4, r5, r6, r7)


def _validate8_helper(
    state: Result[Callable[[A, B, C, D, E, F, G, H], I], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Result[H, FailT],
) -> Result[I, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[B, C, D, E, F, G, H], I], Tuple[FailT, ...]
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
    state: Result[Callable[[A, B, C, D, E, F, G, H, I], J], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Result[H, FailT],
    r9: Result[I, FailT],
) -> Result[J, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[B, C, D, E, F, G, H, I], J], Tuple[FailT, ...]
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
    state: Result[Callable[[A, B, C, D, E, F, G, H, I, J], K], Tuple[FailT, ...]],
    r1: Result[A, FailT],
    r2: Result[B, FailT],
    r3: Result[C, FailT],
    r4: Result[D, FailT],
    r5: Result[E, FailT],
    r6: Result[F, FailT],
    r7: Result[G, FailT],
    r8: Result[H, FailT],
    r9: Result[I, FailT],
    r10: Result[J, FailT],
) -> Result[K, Tuple[FailT, ...]]:
    if isinstance(r1, Err):
        if isinstance(state, Err):
            next_state: Result[
                Callable[[B, C, D, E, F, G, H, I, J], K], Tuple[FailT, ...]
            ] = Err(state.val + (r1.val,))
        else:
            next_state = Err((r1.val,))
    else:
        if isinstance(state, Err):
            next_state = state
        else:
            next_state = Ok(partial(state.val, r1.val))

    return _validate9_helper(next_state, r2, r3, r4, r5, r6, r7, r8, r9, r10)


class _NotSet:
    pass


_not_set = _NotSet()

_Settable = Union[A, _NotSet]


@overload
def _typed_tuple(v1: A) -> Tuple[A]:
    ...


@overload
def _typed_tuple(v1: A, v2: B) -> Tuple[A, B]:
    ...


@overload
def _typed_tuple(v1: A, v2: B, v3: C) -> Tuple[A, B, C]:
    ...


@overload
def _typed_tuple(v1: A, v2: B, v3: C, v4: D) -> Tuple[A, B, C, D]:
    ...


@overload
def _typed_tuple(v1: A, v2: B, v3: C, v4: D, v5: E) -> Tuple[A, B, C, D, E]:
    ...


@overload
def _typed_tuple(v1: A, v2: B, v3: C, v4: D, v5: E, v6: F) -> Tuple[A, B, C, D, E, F]:
    ...


@overload
def _typed_tuple(
    v1: A, v2: B, v3: C, v4: D, v5: E, v6: F, v7: G
) -> Tuple[A, B, C, D, E, F, G]:
    ...


@overload
def _typed_tuple(
    v1: A, v2: B, v3: C, v4: D, v5: E, v6: F, v7: G, v8: H
) -> Tuple[A, B, C, D, E, F, G, H]:
    ...


def _typed_tuple(
    v1: A,
    v2: _Settable[B] = _not_set,
    v3: _Settable[C] = _not_set,
    v4: _Settable[D] = _not_set,
    v5: _Settable[E] = _not_set,
    v6: _Settable[F] = _not_set,
    v7: _Settable[G] = _not_set,
    v8: _Settable[H] = _not_set,
) -> Union[
    Tuple[A],
    Tuple[A, B],
    Tuple[A, B, C],
    Tuple[A, B, C, D],
    Tuple[A, B, C, D, E],
    Tuple[A, B, C, D, E, F],
    Tuple[A, B, C, D, E, F, G],
    Tuple[A, B, C, D, E, F, G, H],
]:
    if isinstance(v2, _NotSet):
        return (v1,)
    elif isinstance(v3, _NotSet):
        return v1, v2
    elif isinstance(v4, _NotSet):
        return v1, v2, v3
    elif isinstance(v5, _NotSet):
        return v1, v2, v3, v4
    elif isinstance(v6, _NotSet):
        return v1, v2, v3, v4, v5
    elif isinstance(v7, _NotSet):
        return v1, v2, v3, v4, v5, v6
    elif isinstance(v8, _NotSet):
        return v1, v2, v3, v4, v5, v6, v7
    else:
        return v1, v2, v3, v4, v5, v6, v7, v8
