from typing import TYPE_CHECKING, Any, Dict, Hashable, List, Optional, Tuple

from koda import nothing

from koda_validate.base import (
    InvalidDict,
    InvalidExtraKeys,
    InvalidMissingKey,
    InvalidType,
    Processor,
    ValidationErr,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)


def validate_dict_to_tuple(
    source_validator: Validator[Any, Any],
    preprocessors: Optional[List[Processor[Dict[Any, Any]]]],
    fast_keys: List[Tuple[Hashable, Validator[Any, Any], bool, bool]],
    schema: Dict[Any, Validator[Any, Any]],
    unknown_keys_err: Tuple[bool, InvalidExtraKeys],
    data: Any,
) -> _ResultTupleUnsafe:
    if not isinstance(data, dict):
        return False, InvalidType(source_validator, dict)

    if preprocessors:
        for preproc in preprocessors:
            data = preproc(data)

    # this seems to be faster than `for key_ in data.keys()`
    for key_ in data:
        if key_ not in schema:
            return unknown_keys_err

    success_dict: Dict[Hashable, Any] = {}
    errs: Dict[Hashable, ValidationErr] = {}
    for key_, validator, key_required, is_tuple_validator in fast_keys:
        try:
            val = data[key_]
        except KeyError:
            if key_required:
                errs[key_] = InvalidMissingKey(source_validator)
            elif not errs:
                success_dict[key_] = nothing
        else:
            if is_tuple_validator:
                if TYPE_CHECKING:
                    assert isinstance(validator, _ToTupleValidatorUnsafe)
                success, new_val = validator.validate_to_tuple(val)
            else:
                success, new_val = (
                    (True, result_.val)
                    if (result_ := validator(val)).is_valid
                    else (False, result_.val)
                )

            if not success:
                errs[key_] = new_val
            elif not errs:
                success_dict[key_] = new_val

    if errs:
        return False, InvalidDict(source_validator, errs)
    else:
        return True, success_dict


async def validate_dict_to_tuple_async(
    source_validator: Validator[Any, Any],
    preprocessors: Optional[List[Processor[Dict[Any, Any]]]],
    fast_keys: List[Tuple[Hashable, Validator[Any, Any], bool, bool]],
    schema: Dict[Any, Validator[Any, Any]],
    unknown_keys_err: Tuple[bool, InvalidExtraKeys],
    data: Any,
) -> _ResultTupleUnsafe:
    if not isinstance(data, dict):
        return False, InvalidType(source_validator, dict)

    if preprocessors:
        for preproc in preprocessors:
            data = preproc(data)

    # this seems to be faster than `for key_ in data.keys()`
    for key_ in data:
        if key_ not in schema:
            return unknown_keys_err

    success_dict: Dict[Hashable, Any] = {}
    errs: Dict[Hashable, ValidationErr] = {}
    for key_, validator, key_required, is_tuple_validator in fast_keys:
        try:
            val = data[key_]
        except KeyError:
            if key_required:
                errs[key_] = InvalidMissingKey(source_validator)
            elif not errs:
                success_dict[key_] = nothing
        else:
            if is_tuple_validator:
                if TYPE_CHECKING:
                    assert isinstance(validator, _ToTupleValidatorUnsafe)
                success, new_val = await validator.validate_to_tuple_async(val)
            else:
                success, new_val = (
                    (True, result_.val)
                    if (result_ := await validator.validate_async(val)).is_valid
                    else (False, result_.val)
                )

            if not success:
                errs[key_] = new_val
            elif not errs:
                success_dict[key_] = new_val

    if errs:
        return False, InvalidDict(source_validator, errs)
    else:
        return True, success_dict
