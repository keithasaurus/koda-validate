from __future__ import annotations

from typing import Iterable, List

from koda import Err, Ok, Result

from koda_validate._generics import A, FailT
from koda_validate.typedefs import Predicate, Serializable


def expected(val: str) -> str:
    return f"expected {val}"


def accum_errors(
    val: A, validators: Iterable[Predicate[A, FailT]]
) -> Result[A, List[FailT]]:
    errors: List[FailT] = []
    for validator in validators:
        result = validator(val)
        if isinstance(result, Err):
            errors.append(result.val)

    if len(errors) > 0:
        return Err(errors)
    else:
        # has to be because there are no errors
        return Ok(val)


def accum_errors_serializable(
    val: A, validators: Iterable[Predicate[A, Serializable]]
) -> Result[A, Serializable]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return accum_errors(val, validators)


def _variant_errors(*variants: Serializable) -> Serializable:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


OBJECT_ERRORS_FIELD = "__container__"
