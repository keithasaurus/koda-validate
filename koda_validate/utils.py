from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Iterable, List, Optional, cast

from koda import Err, Ok, Result

from koda_validate._generics import A, FailT
from koda_validate.typedefs import Predicate, Serializable


def expected(val: str) -> str:
    return f"expected {val}"


def accum_errors(
    val: A, validators: Iterable[Predicate[A, FailT]]
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
        if TYPE_CHECKING:
            assert isinstance(result, Ok)
        return Ok(result.val)


def accum_errors_serializable(
    val: A, validators: Iterable[Predicate[A, Serializable]]
) -> Result[A, Serializable]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return cast(Result[A, Serializable], accum_errors(val, validators))


def _variant_errors(*variants: Serializable) -> Serializable:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Result[A, FailT]]],
    r: Result[A, FailT],
) -> Result[A, FailT]:
    if fn is None:
        return r
    else:
        # optimizing by not using flatmap
        if isinstance(r, Err):
            return r
        else:
            return fn(r.val)


OBJECT_ERRORS_FIELD = "__container__"
