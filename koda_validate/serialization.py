from typing import Dict, List, Tuple, Union

from koda_validate.base import (
    InvalidCoercion,
    InvalidCustom,
    InvalidDict,
    InvalidExtraKeys,
    InvalidIterable,
    InvalidKeyMissing,
    InvalidMap,
    InvalidType,
    InvalidVariants,
    ValidationErr,
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


def serializable_validation_err(err: ValidationErr) -> Serializable:
    if isinstance(err, InvalidCoercion):
        return [err.err_message]
    elif isinstance(err, InvalidCustom):
        return [err.err_message]
    elif isinstance(err, InvalidExtraKeys):
        return [err.err_message]
    elif isinstance(err, InvalidType):
        return [err.err_message]
    elif isinstance(err, list):
        return [p.err_message for p in err]
    elif isinstance(err, InvalidIterable):
        return [[i, serializable_validation_err(err)] for i, err in err.indexes.items()]
    elif isinstance(err, InvalidKeyMissing):
        return ["key missing"]
    elif isinstance(err, InvalidMap):
        errs_dict: Dict[str, Serializable] = {}
        for key, k_v_errs in err.keys.items():
            kv_dict: Dict[str, Serializable] = {
                k: serializable_validation_err(v)
                for k, v in [("key", k_v_errs.key), ("value", k_v_errs.val)]
                if v is not None
            }
            errs_dict[str(key)] = kv_dict
        return errs_dict
    elif isinstance(err, InvalidDict):
        return {str(k): serializable_validation_err(v) for k, v in err.keys.items()}
    elif isinstance(err, InvalidVariants):
        return {"variants": [serializable_validation_err(x) for x in err.variants]}
    else:
        raise TypeError(f"got unhandled type: {type(err)}")
