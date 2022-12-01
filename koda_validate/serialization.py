from typing import Any, Dict, List, Tuple, Union

from koda_validate.base import (
    BasicErr,
    CoercionErr,
    DictErr,
    ExtraKeysErr,
    Invalid,
    IterableErr,
    MapErr,
    MissingKeyErr,
    Predicate,
    PredicateAsync,
    PredicateErrs,
    TypeErr,
    VariantErrs,
)
from koda_validate.dictionary import MaxKeys, MinKeys
from koda_validate.generic import (
    Choices,
    EqualTo,
    ExactItemCount,
    Max,
    MaxItems,
    Min,
    MinItems,
    MultipleOf,
    UniqueItems,
)
from koda_validate.string import (
    EmailPredicate,
    MaxLength,
    MinLength,
    NotBlank,
    RegexPredicate,
)

Serializable = Union[
    None,
    int,
    str,
    bool,
    float,
    List["Serializable"],
    Tuple["Serializable", ...],
    Dict[str, "Serializable"],
]


def pred_to_err_message(pred: Union[Predicate[Any], PredicateAsync[Any]]) -> str:
    if isinstance(pred, MinKeys):
        return f"minimum allowed properties is {pred.size}"
    elif isinstance(pred, MaxKeys):
        return f"maximum allowed properties is {pred.size}"
    elif isinstance(pred, Choices):
        return f"expected one of {sorted(pred.choices)}"
    elif isinstance(pred, Min):
        exclusive = " (exclusive)" if pred.exclusive_minimum else ""
        return f"minimum allowed value{exclusive} is {pred.minimum}"
    elif isinstance(pred, Max):
        exclusive = " (exclusive)" if pred.exclusive_maximum else ""
        return f"maximum allowed value{exclusive} is {pred.maximum}"
    elif isinstance(pred, MultipleOf):
        return f"expected multiple of {pred.factor}"
    elif isinstance(pred, EqualTo):
        return f"must equal {repr(pred.match)}"
    elif isinstance(pred, MinItems):
        return f"minimum allowed length is {pred.length}"
    elif isinstance(pred, MaxItems):
        return f"maximum allowed length is {pred.length}"
    elif isinstance(pred, ExactItemCount):
        return f"length must be {pred.length}"
    elif isinstance(pred, UniqueItems):
        return "all items must be unique"
    elif isinstance(pred, RegexPredicate):
        return rf"must match pattern {pred.pattern.pattern}"
    elif isinstance(pred, EmailPredicate):
        return "expected a valid email address"
    elif isinstance(pred, NotBlank):
        return "cannot be blank"
    elif isinstance(pred, MinLength):
        return f"minimum allowed length is {pred.length}"
    elif isinstance(pred, MaxLength):
        return f"maximum allowed length is {pred.length}"
    else:
        raise TypeError(f"unhandled type: {type(pred)}")


def serializable_validation_err(invalid: Invalid) -> Serializable:
    err = invalid.err_type
    if isinstance(err, CoercionErr):
        compatible_names = [t.__name__ for t in err.compatible_types]
        return [
            f"could not coerce to {err.dest_type.__name__} "
            f"(compatible with {', '.join(compatible_names)})"
        ]
    elif isinstance(err, BasicErr):
        return [err.err_message]
    elif isinstance(err, ExtraKeysErr):
        err_message = "Received unknown keys. " + (
            "Expected empty dictionary."
            if len(err.expected_keys) == 0
            else "Only expected "
            + ", ".join(sorted([repr(k) for k in err.expected_keys]))
            + "."
        )
        return [err_message]
    elif isinstance(err, TypeErr):
        return [f"expected {err.expected_type.__name__}"]
    elif isinstance(err, PredicateErrs):
        return [pred_to_err_message(p) for p in err.predicates]
    elif isinstance(err, IterableErr):
        return [[i, serializable_validation_err(err)] for i, err in err.indexes.items()]
    elif isinstance(err, MissingKeyErr):
        return ["key missing"]
    elif isinstance(err, MapErr):
        errs_dict: Dict[str, Serializable] = {}
        for key, k_v_errs in err.keys.items():
            kv_dict: Dict[str, Serializable] = {
                k: serializable_validation_err(v)
                for k, v in [("key", k_v_errs.key), ("value", k_v_errs.val)]
                if v is not None
            }
            errs_dict[str(key)] = kv_dict
        return errs_dict
    elif isinstance(err, DictErr):
        return {str(k): serializable_validation_err(v) for k, v in err.keys.items()}
    elif isinstance(err, VariantErrs):
        return {"variants": [serializable_validation_err(x) for x in err.variants]}
    else:
        raise TypeError(f"got unhandled type: {type(err)}")
