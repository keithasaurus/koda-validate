from __future__ import annotations

from typing import Callable, Final, Iterable, List, Optional

from koda import Err, Ok, Result

from koda_validate._generics import A, FailT
from koda_validate.typedefs import Predicate, Serializable


def accum_errors(
    val: A, validators: Iterable[Predicate[A, Serializable]]
) -> Result[A, Serializable]:
    errors: List[Serializable] = [
        result.val
        for validator in validators
        if isinstance(result := validator(val), Err)
    ]

    if len(errors) > 0:
        result = Err(errors)
    else:
        # has to be original val because there are no
        # errors, and predicates prevent there from being
        # modification to the value
        result = Ok(val)
    return result


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


OBJECT_ERRORS_FIELD: Final[str] = "__container__"
