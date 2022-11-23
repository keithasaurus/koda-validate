from typing import Any, Final, Optional

from koda._generics import A

from koda_validate.base import (
    InvalidType,
    InvalidVariants,
    ValidationErr,
    ValidationResult,
    Validator,
)
from koda_validate.validated import Invalid, Valid

OK_NONE: Final[Valid[None]] = Valid(None)
OK_NONE_OPTIONAL: Final[Valid[Optional[Any]]] = Valid(None)

EXPECTED_NONE_ERR: Final[ValidationErr] = InvalidType(type(None), "expected None")
EXPECTED_NONE: Final[Invalid[ValidationErr]] = Invalid(EXPECTED_NONE_ERR)


class OptionalValidator(Validator[Any, Optional[A]]):
    """
    We have a value for a key, but it can be null (None)
    """

    __slots__ = ("validator",)
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[Any, A]) -> None:
        self.validator = validator

    def __call__(self, val: Any) -> ValidationResult[Optional[A]]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: ValidationResult[A] = self.validator(val)
            if result.is_valid:
                return Valid(result.val)
            else:
                return Invalid(InvalidVariants([EXPECTED_NONE_ERR, result.val]))

    async def validate_async(self, val: Any) -> ValidationResult[Optional[A]]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: ValidationResult[A] = await self.validator.validate_async(val)
            if result.is_valid:
                return Valid(result.val)
            else:
                return Invalid(InvalidVariants([EXPECTED_NONE_ERR, result.val]))


class NoneValidator(Validator[Any, None]):
    def __call__(self, val: Any) -> ValidationResult[None]:
        if val is None:
            return OK_NONE
        else:
            return EXPECTED_NONE

    async def validate_async(self, val: Any) -> ValidationResult[None]:
        return self(val)


none_validator = NoneValidator()
