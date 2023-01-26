from dataclasses import dataclass
from typing import Any, Callable, Generic, Set, Type

from koda import Maybe

from koda_validate._generics import A


@dataclass
class Coercer(Generic[A]):
    coerce: Callable[[Any], Maybe[A]]
    """
    The function which handles the coercion.
    """
    compatible_types: Set[Type[Any]]
    """
    All the types which can potentially be coerced.
    """

    def __call__(self, val: Any) -> Maybe[A]:
        return self.coerce(val)


def coercer(
    *compatible_types: Type[Any],
) -> Callable[[Callable[[Any], Maybe[A]]], Coercer[A]]:
    """
    This is purely a convenience constructor for :class:`Coercer` objects.

    :param compatible_types: the types the coercer can take to produce an
        the return type
    :return: A callable which accepts a function that should be congruent
        with the ``compatible_types`` param.

    """

    def inner(func: Callable[[Any], Maybe[A]]) -> Coercer[A]:
        return Coercer(func, set(compatible_types))

    return inner
