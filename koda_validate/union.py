from typing import Any, Tuple

from koda_validate._internal import ResultTuple, _ToTupleValidator
from koda_validate.base import Invalid, Validator, VariantErrs


class UnionValidatorAny(_ToTupleValidator[Any]):
    """
    Until we're comfortable using variadic args, we'll just keep this private
    """

    __match_args__ = ("validators",)

    def __init__(
        self,
        # just a way to enforce at least one validator is defined
        validator_1: Validator[Any],
        *validators: Validator[Any],
    ) -> None:
        self.validators: Tuple[Validator[Any], ...] = (validator_1,) + validators

    def validate_to_tuple(self, val: Any) -> ResultTuple[Any]:
        errs = []
        for validator in self.validators:
            if isinstance(validator, _ToTupleValidator):
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
                    errs.append(result)
        return False, Invalid(self, val, VariantErrs(errs))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Any]:
        errs = []
        for validator in self.validators:
            if isinstance(validator, _ToTupleValidator):
                success, new_val = await validator.validate_to_tuple_async(val)
                if success:
                    return True, new_val
                else:
                    errs.append(new_val)
            else:
                result = await validator.validate_async(val)
                if result.is_valid:
                    return True, result.val
                else:
                    errs.append(result)
        return False, Invalid(self, val, VariantErrs(errs))
