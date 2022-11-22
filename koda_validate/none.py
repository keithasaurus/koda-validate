from types import NoneType
from typing import Any, Final, Optional

from koda._generics import A

from koda_validate._internals import _variant_errors
from koda_validate.base import (
    CoercionErr,
    Serializable,
    TypeErr,
    ValidationErr,
    Validator,
    VariantErrs,
)
from koda_validate.validated import Invalid, Valid, Validated

OK_NONE: Final[Valid[None]] = Valid(None)
OK_NONE_OPTIONAL: Final[Valid[Optional[Any]]] = Valid(None)

EXPECTED_NONE_ERR: Final[ValidationErr] = TypeErr(NoneType, "expected None")
EXPECTED_NONE: Final[Invalid[ValidationErr]] = Invalid([EXPECTED_NONE_ERR])


class OptionalValidator(Validator[Any, Optional[A]]):
    """
    We have a value for a key, but it can be null (None)
    """

    __slots__ = ("validator",)
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[Any, A]) -> None:
        self.validator = validator

    def __call__(self, val: Any) -> Validated[Optional[A], ValidationErr]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: Validated[A, ValidationErr] = self.validator(val)
            if result.is_valid:
                return Valid(result.val)
            else:
                return Invalid(VariantErrs([EXPECTED_NONE_ERR, result.val]))

    async def validate_async(self, val: Any) -> Validated[Optional[A], ValidationErr]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: Validated[A, Serializable] = await self.validator.validate_async(val)
            if result.is_valid:
                return Valid(result.val)
            else:
                return Invalid(VariantErrs([EXPECTED_NONE_ERR, result.val]))


class NoneValidator(Validator[Any, None]):
    def __call__(self, val: Any) -> Validated[None, ValidationErr]:
        if val is None:
            return OK_NONE
        else:
            return EXPECTED_NONE

    async def validate_async(self, val: Any) -> Validated[None, ValidationErr]:
        return self(val)


none_validator = NoneValidator()
