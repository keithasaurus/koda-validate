from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Final, Iterable, List, Optional, cast

from koda import Err, Ok, Result

from koda_validate._cruft import _chain
from koda_validate._generics import A, FailT
from koda_validate.typedefs import JSONValue, Predicate


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


chain = _chain


def accum_errors_json(
    val: A, validators: Iterable[Predicate[A, JSONValue]]
) -> Result[A, JSONValue]:
    """
    Helper that exists only because mypy is not always great at narrowing types
    """
    return cast(Result[A, JSONValue], accum_errors(val, validators))


def _variant_errors(*variants: JSONValue) -> JSONValue:
    return {f"variant {i + 1}": v for i, v in enumerate(variants)}


def _flat_map_same_type_if_not_none(
    fn: Optional[Callable[[A], Result[A, FailT]]],
    r: Result[A, FailT],
) -> Result[A, FailT]:
    if fn is None:
        return r
    else:
        return r.flat_map(fn)


OBJECT_ERRORS_FIELD = "__container__"
