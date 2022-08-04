from __future__ import annotations

from typing import Callable, Optional, Tuple, Union, overload

from koda.result import Result

from koda_validate._generics import A, B, C, D, E, F, FailT, G, H

# simple alias allows to greatly reduce amount of characters required to define
from koda_validate.typedefs import ValidatorFunc


@overload
def _chain(
    fn1: ValidatorFunc[A, B, FailT], fn2: ValidatorFunc[B, C, FailT]
) -> ValidatorFunc[A, C, FailT]:
    ...


@overload
def _chain(
    fn1: ValidatorFunc[A, B, FailT],
    fn2: ValidatorFunc[B, C, FailT],
    fn3: ValidatorFunc[C, D, FailT],
) -> ValidatorFunc[A, D, FailT]:
    ...


@overload
def _chain(
    fn1: ValidatorFunc[A, B, FailT],
    fn2: ValidatorFunc[B, C, FailT],
    fn3: ValidatorFunc[C, D, FailT],
    fn4: ValidatorFunc[D, E, FailT],
) -> ValidatorFunc[A, E, FailT]:
    ...


@overload
def _chain(
    fn1: ValidatorFunc[A, B, FailT],
    fn2: ValidatorFunc[B, C, FailT],
    fn3: ValidatorFunc[C, D, FailT],
    fn4: ValidatorFunc[D, E, FailT],
    fn5: ValidatorFunc[E, F, FailT],
) -> ValidatorFunc[A, F, FailT]:
    ...


@overload
def _chain(
    fn1: ValidatorFunc[A, B, FailT],
    fn2: ValidatorFunc[B, C, FailT],
    fn3: ValidatorFunc[C, D, FailT],
    fn4: ValidatorFunc[D, E, FailT],
    fn5: ValidatorFunc[E, F, FailT],
    fn6: ValidatorFunc[F, G, FailT],
) -> ValidatorFunc[A, G, FailT]:
    ...


def _chain(
    fn1: ValidatorFunc[A, B, FailT],
    fn2: ValidatorFunc[B, C, FailT],
    fn3: Optional[ValidatorFunc[C, D, FailT]] = None,
    fn4: Optional[ValidatorFunc[D, E, FailT]] = None,
    fn5: Optional[ValidatorFunc[E, F, FailT]] = None,
    fn6: Optional[ValidatorFunc[F, G, FailT]] = None,
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


# todo: auto-generate
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
