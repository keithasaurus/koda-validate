from __future__ import annotations

from typing import Iterable, List

from koda import Err, Ok, Result

from koda_validate._cruft import _chain, _validate_and_map
from koda_validate._generics import A, FailT
from koda_validate.serialization import JsonSerializable
from koda_validate.typedefs import JO, PredicateValidator


def expected(val: str) -> str:
    return f"expected {val}"


def accum_errors(
    val: A, validators: Iterable[PredicateValidator[A, FailT]]
) -> Result[A, List[FailT]]:
    errors: List[FailT] = []
    result: Result[A, FailT] = Ok(val)
    for validator in validators:
        result = validator(val)
        if isinstance(result, Err):
            errors.append(result.val)
        else:
            val = result.val

    if len(errors) > 0:
        return Err(errors)
    else:
        # has to be because there are no errors
        assert isinstance(result, Ok)
        return Ok(result.val)


chain = _chain
validate_and_map = _validate_and_map


def unwrap_jsonable(data: JO) -> JsonSerializable:
    """
    todo: consider moving away from recursive
    """
    if isinstance(data.val, str):
        return data.val
    elif isinstance(data.val, bool):
        return data.val
    elif isinstance(data.val, int):
        return data.val
    elif isinstance(data.val, float):
        return data.val
    elif data.val is None:
        return None
    elif isinstance(data.val, list):
        return [unwrap_jsonable(item) for item in data.val]
    elif isinstance(data.val, tuple):
        return tuple(unwrap_jsonable(item) for item in data.val)
    else:
        assert isinstance(data.val, dict)
        return {k: unwrap_jsonable(val) for k, val in data.val.items()}
