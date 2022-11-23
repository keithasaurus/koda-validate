from koda_validate.base import (
    InvalidDict,
    InvalidIterable,
    InvalidKeyMissing,
    InvalidType,
    Serializable,
    ValidationErr,
)


def serializable_validation_err(err: ValidationErr) -> Serializable:
    match err:
        case InvalidType(type_):
            return f"expected type {type_}"
        case [*predicates]:
            return [p.err_message for p in predicates]
        case InvalidIterable(errs):
            return [[i, serializable_validation_err(err)] for i, err in errs.items()]
        case InvalidDict(key_errs):
            return {str(k): serializable_validation_err(v) for k, v in key_errs.items()}
        case InvalidKeyMissing():
            return "key_missing"

        case _:
            raise TypeError(f"got unhandled type: {type(err)}")
        # case DictErrs(errs):
