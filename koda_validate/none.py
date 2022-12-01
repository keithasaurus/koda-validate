from typing import Any, Final, Optional

from koda._generics import A

from koda_validate import Valid
from koda_validate._internal import _ExactTypeValidator
from koda_validate.base import ValidationResult, Validator
from koda_validate.union import UnionValidatorAny

OK_NONE: Final[Valid[None]] = Valid(None)
OK_NONE_OPTIONAL: Final[Valid[Optional[Any]]] = Valid(None)


class NoneValidator(_ExactTypeValidator[None]):
    _TYPE = type(None)


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
