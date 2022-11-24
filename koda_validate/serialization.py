from typing import Dict

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
    Serializable,
    ValidationErr,
)


def serializable_validation_err(err: ValidationErr) -> Serializable:
    match err:
        case InvalidCoercion(_, _, err_message):
            return [err_message]
        case InvalidCustom(err_message):
            return [err_message]
        case InvalidExtraKeys(_, err_message):
            return [err_message]
        case InvalidType(_, err_message):
            return [err_message]
        case [*predicates]:
            return [p.err_message for p in predicates]
        case InvalidIterable(errs):
            return [[i, serializable_validation_err(err)] for i, err in errs.items()]
        case InvalidDict(key_errs):
            return {str(k): serializable_validation_err(v) for k, v in key_errs.items()}
        case InvalidKeyMissing():
            return ["key missing"]
        case InvalidMap(key_val_errs):
            errs_dict: Dict[str, Serializable] = {}
            for key, k_v_errs in key_val_errs.items():
                kv_dict: Dict[str, Serializable] = {
                    k: serializable_validation_err(v)
                    for k, v in [("key", k_v_errs.key), ("value", k_v_errs.val)]
                    if v is not None
                }
                errs_dict[str(key)] = kv_dict
            return errs_dict
        case InvalidVariants(variants):
            return {"variants": [serializable_validation_err(x) for x in variants]}

        case _:
            raise TypeError(f"got unhandled type: {type(err)}")
