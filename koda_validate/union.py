from typing import Any, Tuple

from koda_validate.base import (
    InvalidVariants,
    Validator,
    _ResultTupleUnsafe,
    _ToTupleValidatorUnsafe,
)


class UnionValidatorAny(_ToTupleValidatorUnsafe[Any, Any]):
    """
    Until we're comfortable using variadic args, we'll just keep this private
    """

    def __init__(
        self,
        # just a way to enforce at least one validator is defined
        validator_1: Validator[Any, Any],
        *validators: Validator[Any, Any],
    ) -> None:
        self.validators: Tuple[Validator[Any, Any], ...] = (validator_1,) + validators

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
        return False, InvalidVariants(errs)
