from typing import Any, Final, Optional

from koda._generics import A

from koda_validate._internals import _variant_errors
from koda_validate.typedefs import Invalid, Serializable, Valid, Validated, Validator

OK_NONE: Final[Valid[None]] = Valid(None)
OK_NONE_OPTIONAL: Final[Valid[Optional[Any]]] = Valid(None)


class OptionalValidator(Validator[Any, Optional[A], Serializable]):
    """
    We have a value for a key, but it can be null (None)
    """

    __slots__ = ("validator",)
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def __call__(self, val: Any) -> Validated[Optional[A], Serializable]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: Validated[A, Serializable] = self.validator(val)
            if result.is_ok:
                return Valid(result.val)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )

    async def validate_async(self, val: Any) -> Validated[Optional[A], Serializable]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: Validated[A, Serializable] = await self.validator.validate_async(val)
            if result.is_ok:
                return Valid(result.val)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )


EXPECTED_NONE: Final[Invalid[Serializable]] = Invalid(["expected None"])


class NoneValidator(Validator[Any, None, Serializable]):
    def __call__(self, val: Any) -> Validated[None, Serializable]:
        if val is None:
            return OK_NONE
        else:
            return EXPECTED_NONE

    async def validate_async(self, val: Any) -> Validated[None, Serializable]:
        return self(val)


none_validator = NoneValidator()
