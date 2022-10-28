from __future__ import annotations

from typing import Any, Callable, Dict, Final, Generic, Iterable, List, Optional, Tuple

from koda import Err, Just, Maybe, Nothing, Ok, Result

from koda_validate._generics import A, FailT
from koda_validate.typedefs import Predicate, Serializable, Validator


def expected(val: str) -> str:
    return f"expected {val}"


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


_KEY_MISSING: Final[str] = "key missing"

KeyValidator = Tuple[str, Callable[[Maybe[Any]], Result[A, Serializable]]]


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

_is_dict_validation_err: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: [expected("a dictionary")]}
)


def too_many_keys(keys: set[str]) -> Err[Serializable]:
    return Err(
        {OBJECT_ERRORS_FIELD: [f"Received unknown keys. Only expected {sorted(keys)}"]}
    )


def _tuples_to_json_dict(data: List[Tuple[str, Serializable]]) -> Serializable:
    return dict(data)


class RequiredField(Generic[A]):
    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[A, Serializable]:
        if isinstance(maybe_val, Nothing):
            return Err([_KEY_MISSING])
        else:
            return self.validator(maybe_val.val)


class MaybeField(Generic[A]):
    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def __call__(self, maybe_val: Maybe[Any]) -> Result[Maybe[A], Serializable]:
        if isinstance(maybe_val, Just):
            result: Result[Maybe[A], Serializable] = self.validator(maybe_val.val).map(
                Just
            )
        else:
            result = Ok(maybe_val)
        return result


def key(
    prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[A, Serializable]]]:
    return prop_, RequiredField(validator)


def maybe_key(
    prop_: str, validator: Validator[Any, A, Serializable]
) -> Tuple[str, Callable[[Any], Result[Maybe[A], Serializable]]]:
    return prop_, MaybeField(validator)
