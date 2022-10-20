from typing import Callable, Final, Optional

from koda import Result

from koda_validate._generics import A, FailT

CONTAINER_KEY: Final[str] = "__container__"


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Result[A, FailT]]],
    r: Result[A, FailT],
) -> Result[A, FailT]:
    if fn is None:
        return r
    else:
        return r.flat_map(fn)
