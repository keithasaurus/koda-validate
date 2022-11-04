from typing import Any, Final, Optional

from koda import Err, Ok, Result
from koda._generics import A

from koda_validate._internals import _variant_errors
from koda_validate.typedefs import Serializable, Validator

OK_NONE: Final[Ok[None]] = Ok(None)
OK_NONE_OPTIONAL: Final[Ok[Optional[Any]]] = Ok(None)


class OptionalValidator(Validator[Any, Optional[A], Serializable]):
    """
    We have a value for a key, but it can be null (None)
    """

    __slots__ = ("validator",)
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def __call__(self, val: Any) -> Result[Optional[A], Serializable]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: Result[A, Serializable] = self.validator(val)
            if result.is_ok:
                return Ok(result.val)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )

    async def validate_async(self, val: Any) -> Result[Optional[A], Serializable]:
        if val is None:
            return OK_NONE_OPTIONAL
        else:
            result: Result[A, Serializable] = await self.validator.validate_async(val)
            if result.is_ok:
                return Ok(result.val)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )


EXPECTED_NONE: Final[Err[Serializable]] = Err(["expected None"])


class NoneValidator(Validator[Any, None, Serializable]):
    def __call__(self, val: Any) -> Result[None, Serializable]:
        if val is None:
            return OK_NONE
        else:
            return EXPECTED_NONE

    async def validate_async(self, val: Any) -> Result[None, Serializable]:
        return self(val)


none_validator = NoneValidator()
