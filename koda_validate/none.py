from typing import Any, Optional

from koda._generics import A

from koda_validate._internal import _ExactTypeValidator, _ToTupleValidator, ResultTuple
from koda_validate.base import ValidationResult, Validator, Invalid, TypeErr
from koda_validate.union import UnionValidatorAny


class NoneValidator(_ToTupleValidator[None]):
    def validate_to_tuple(self, val: Any) -> ResultTuple[None]:
        if val is None:
            return True, None
        else:
            return False, Invalid(self, TypeErr(type(None)))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[None]:
        return self.validate_to_tuple(val)


none_validator = NoneValidator()


class OptionalValidator(Validator[Optional[A]]):
    """
    We have a value for a key, but it can be null (None)
    """

    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[A]) -> None:
        self.validator = UnionValidatorAny(none_validator, validator)

    async def validate_async(self, val: Any) -> ValidationResult[Optional[A]]:
        result = await self.validator.validate_async(val)
        if result.is_valid:
            return result
        else:
            result.validator = self
            return result

    def __call__(self, val: Any) -> ValidationResult[Optional[A]]:
        result = self.validator(val)
        if result.is_valid:
            return result
        else:
            result.validator = self
            return result
