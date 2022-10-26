from typing import Any, Callable, List, Optional, Tuple, TypeVar

from koda import Err, Ok, Result

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


def validate_and_map(
    into: Callable[..., Ret],
    # this could be handled better with variadic generics
    *fields: Tuple[bool, Tuple[str, FailT]],
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, List[FailT]]:
    args = []
    errs = []
    for valid, val in fields:
        if valid:
            args.append(val)
        else:
            errs.append(val)

    if len(errs) > 0:
        return Err(errs)
    else:
        obj = into(*args)
        if validate_object is None:
            return Ok(obj)
        else:
            result = validate_object(obj)
            if isinstance(result, Ok):
                return result
            else:
                return Err([result.val])
