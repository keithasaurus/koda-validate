from typing import Callable, ClassVar, Final, Optional

from koda_validate._generics import A, FailT
from koda_validate.validated import Validated


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Validated[A, FailT]]],
    r: Validated[A, FailT],
) -> Validated[A, FailT]:
    if fn is None:
        return r
    else:
        if not r.is_valid:
            return r
        else:
            return fn(r.val)


OBJECT_ERRORS_FIELD: Final[str] = "__container__"


class _NotSet:
    _instance: ClassVar[Optional["_NotSet"]] = None

    def __new__(cls) -> "_NotSet":
        """
        Make a singleton, so we can do `is` checks if we want.
        """
        if cls._instance is None:
            cls._instance = super(_NotSet, cls).__new__(cls)
        return cls._instance


_not_set = _NotSet()
