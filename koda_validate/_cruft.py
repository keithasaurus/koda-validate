from __future__ import annotations

from typing import Tuple, Union, overload

from koda_validate._generics import A, B, C


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


# todo: auto-generate
def _typed_tuple(
    v1: A,
    v2: _Settable[B] = _not_set,
    v3: _Settable[C] = _not_set,
) -> Union[Tuple[A], Tuple[A, B], Tuple[A, B, C]]:
    if isinstance(v2, _NotSet):
        return (v1,)
    elif isinstance(v3, _NotSet):
        return v1, v2
    else:
        return v1, v2, v3
