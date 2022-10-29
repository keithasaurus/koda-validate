from __future__ import annotations

from typing import Tuple, Union, overload

from koda_validate._generics import A, B, C, D, E, F, G, H


class _NotSet:
    pass


_not_set = _NotSet()

_Settable = Union[A, _NotSet]


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
