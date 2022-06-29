from __future__ import annotations

from typing import Iterable

from koda import Err, Ok, Result

from koda_validate._cruft import _chain, _validate_and_map
from koda_validate._generics import A, FailT
from koda_validate.typedefs import PredicateValidator


def expected(val: str) -> str:
    return f"expected {val}"


def accum_errors(
    val: A, validators: Iterable[PredicateValidator[A, FailT]]
) -> Result[A, list[FailT]]:
    errors: list[FailT] = []
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
