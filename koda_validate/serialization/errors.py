from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Dict, Optional, Type, Union

from koda_validate import NotBlank
from koda_validate.base import Predicate, PredicateAsync
from koda_validate.dataclasses import DataclassValidator
from koda_validate.decimal import DecimalValidator
from koda_validate.dictionary import MaxKeys, MinKeys
from koda_validate.errors import (
    CoercionErr,
    ContainerErr,
    ExtraKeysErr,
    IndexErrs,
    KeyErrs,
    MapErr,
    MissingKeyErr,
    PredicateErrs,
    SetErrs,
    TypeErr,
    UnionErrs,
    ValidationErrBase,
)
from koda_validate.generic import (
    Choices,
    EndsWith,
    EqualTo,
    ExactItemCount,
    ExactLength,
    Max,
    MaxItems,
    MaxLength,
    Min,
    MinItems,
    MinLength,
    MultipleOf,
    StartsWith,
    UniqueItems,
)
from koda_validate.namedtuple import NamedTupleValidator
from koda_validate.serialization.base import Serializable
from koda_validate.string import EmailPredicate, RegexPredicate
from koda_validate.time import DatetimeValidator, DateValidator
from koda_validate.uuid import UUIDValidator
from koda_validate.valid import Invalid


@dataclass
class SerializableErr(ValidationErrBase):
    """
    A validation error where you may simply want to produce a human-readable message.
    """

    obj: Serializable
    """
    The error contents you want to return.
    """


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
        return f"minimum allowed length is {pred.item_count}"
    elif isinstance(pred, MaxItems):
        return f"maximum allowed length is {pred.item_count}"
    elif isinstance(pred, ExactItemCount):
        return f"length must be {pred.item_count}"
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
    elif isinstance(pred, ExactLength):
        return f"expected length of {pred.length}"
    elif isinstance(pred, StartsWith):
        return rf"must start with {repr(pred.prefix)}"
    elif isinstance(pred, EndsWith):
        return rf"must end with {repr(pred.suffix)}"
    else:
        raise TypeError(
            f"Unhandled predicate type: {type(pred)}. You may want to write a wrapper "
            f"function which handles that type."
        )


TYPE_DESCRIPTION_LOOKUP: Dict[Type[Any], str] = {
    str: "string",
    int: "integer",
    Decimal: "decimal",
    bool: "boolean",
    dict: "object",
    list: "array",
    tuple: "array",
}


def to_serializable_errs(
    invalid: Invalid, next_level: Optional[Callable[[Invalid], Serializable]] = None
) -> Serializable:
    """
    Convert an ``Invalid`` instance to human readable (English) ``Serializable``
    representation of ``Invalid``.

    It can serve as an example of how to build similar functions to convert ``Invalid``
    instances to other formats, other languages, etc.

    :param invalid: The error you'd like to represent
    :param next_level: If supplied, this callable will handle any calls for container
        ``ErrType``s such as ``ContainerErr``, ``KeyErr``, and so on

    :return: an error message appropriate for serializing in JSON or YAML. Because this
        function can handle any kind of Invalid, any type narrowing desired beyond
        ``Serializable`` needs to be done outside of this function.

    """
    next_level = next_level or to_serializable_errs
    err = invalid.err_type
    vldtr = invalid.validator
    if isinstance(err, CoercionErr):
        if isinstance(vldtr, UUIDValidator):
            return ["expected a UUID"]
        elif isinstance(vldtr, DecimalValidator):
            return ["expected a decimal-formatted string"]
        elif isinstance(vldtr, DatetimeValidator):
            return ["expected an iso8601 datetime string"]
        elif isinstance(vldtr, DateValidator):
            return ["expected YYYY-MM-DD"]
        elif err.dest_type is list or err.dest_type is tuple:
            return {"__container__": ["expected a list"]}
        elif isinstance(vldtr, (DataclassValidator, NamedTupleValidator)):
            return {"__container__": ["expected a dict"]}
        else:
            compatible_names = sorted([t.__name__ for t in err.compatible_types])
            return [
                f"could not coerce to {err.dest_type.__name__} "
                f"(compatible with {', '.join(compatible_names)})"
            ]
    elif isinstance(err, SerializableErr):
        return err.obj
    elif isinstance(err, ExtraKeysErr):
        err_message = (
            "expected an empty dict"
            if len(err.expected_keys) == 0
            else "only expected "
            + ", ".join(sorted([repr(k) for k in err.expected_keys]))
        )
        return {"__unknown_keys__": err_message}
    elif isinstance(err, TypeErr):
        if err.expected_type is dict:
            return {"__container__": ["expected a dict"]}
        elif err.expected_type is list or err.expected_type is tuple:
            return {"__container__": ["expected a list"]}
        else:
            type_desc = TYPE_DESCRIPTION_LOOKUP.get(
                err.expected_type, err.expected_type.__name__
            )
            if type_desc[0] in {"a", "e", "i", "o", "u"}:
                type_desc = f"an {type_desc}"
            else:
                type_desc = f"a {type_desc}"
            return [f"expected {type_desc}"]
    elif isinstance(err, PredicateErrs):
        return [pred_to_err_message(p) for p in err.predicates]
    elif isinstance(err, IndexErrs):
        return [[i, next_level(err)] for i, err in err.indexes.items()]
    elif isinstance(err, MissingKeyErr):
        return ["key missing"]
    elif isinstance(err, MapErr):
        errs_dict: Dict[str, Serializable] = {}
        for key, k_v_errs in err.keys.items():
            kv_dict: Dict[str, Serializable] = {
                k: next_level(v)
                for k, v in [("key", k_v_errs.key), ("value", k_v_errs.val)]
                if v is not None
            }
            errs_dict[str(key)] = kv_dict
        return errs_dict
    elif isinstance(err, SetErrs):
        return {"member_errors": [next_level(x) for x in err.item_errs]}
    elif isinstance(err, KeyErrs):
        return {str(k): next_level(v) for k, v in err.keys.items()}
    elif isinstance(err, UnionErrs):
        return {"variants": [next_level(x) for x in err.variants]}
    elif isinstance(err, ContainerErr):
        return next_level(err.child)
    else:
        raise TypeError(f"got unhandled type: {type(err)}")
