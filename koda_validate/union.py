from typing import Any, Tuple

from koda_validate._internal import (
    ResultTuple,
    _ToTupleValidator,
    _union_validator,
    _union_validator_async,
)
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
        return _union_validator(self, self.validators, val)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Any]:
        return await _union_validator_async(self, self.validators, val)
