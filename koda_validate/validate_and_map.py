from typing import Any, Callable, List, Optional, Tuple, TypeVar

from koda import Err, Ok, Result

Ret = TypeVar("Ret")
FailT = TypeVar("FailT")


def validate_and_map(
    into: Callable[..., Ret],
    # this could be handled better with variadic generics
    *fields: Result[Any, FailT],
    validate_object: Optional[Callable[[Ret], Result[Ret, FailT]]] = None,
) -> Result[Ret, List[FailT]]:
    args = []
    errs = []
    for f in fields:
        if isinstance(f, Ok):
            if len(errs) == 0:
                args.append(f.val)
        else:
            errs.append(f.val)

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
