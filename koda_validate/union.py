from typing import Any

from koda_validate._internals import _variant_errors
from koda_validate.base import (
    Serializable,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)


class UnionValidatorAny(_ToTupleValidatorUnsafe[Any, Any, Serializable]):
    """
    Until we're comfortable using variadic args, we'll just keep this private
    """

    def __init__(
        self,
        # just a way to enforce at least one validator is defined
        validator_1: Validator[Any, Any, Serializable],
        *validators: Validator[Any, Any, Serializable],
    ) -> None:
        self.validators = (validator_1,) + validators

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        errs = []
        for validator in self.validators:
            if isinstance(validator, _ToTupleValidatorUnsafe):
                success, new_val = validator.validate_to_tuple(val)
                if success:
                    return True, new_val
                else:
                    errs.append(new_val)
            else:
                result = validator(val)
                if result.is_valid:
                    return True, result.val
                else:
                    errs.append(result.val)
        return False, _variant_errors(*errs)
