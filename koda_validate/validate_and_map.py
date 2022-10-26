from typing import Any, Callable, List, Optional, Tuple

from koda import Err, Maybe, Ok, Result, mapping_get
from koda._generics import A

from koda_validate._generics import FailT, Ret
from koda_validate.typedefs import Serializable

KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, Serializable]]]


def _validate_and_map(
    into: Callable[..., Ret],
    data: Any,
    # this could be handled better with variadic generics
    *fields: KeyValidator[Any],
    validate_object: Optional[Callable[[Ret], Result[Ret, Any]]] = None,
) -> Result[Ret, List[FailT]]:
    if not isinstance(data, dict):
        return Err({"err": ["not a dict"]})

    args = []
    errs: List[Tuple[str, FailT]] = []
    for key, validator in fields:
        if key not in data:
            # if we get extra keys, we want to exit as quickly as possible
            return Err({"bad": "keys"})

        result = validator(mapping_get(data, key))

        # (slightly) optimized for no .map_err call
        if isinstance(result, Err):
            errs.append((key, result.val))
        else:
            args.append(result.val)

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
