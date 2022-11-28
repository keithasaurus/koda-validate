from typing import Any, Final, Optional

from koda._generics import A

from koda_validate.base import ValidationResult, Validator, _ExactTypeValidator
from koda_validate.union import UnionValidatorAny
from koda_validate.validated import Valid

OK_NONE: Final[Valid[None]] = Valid(None)
OK_NONE_OPTIONAL: Final[Valid[Optional[Any]]] = Valid(None)


class NoneValidator(_ExactTypeValidator[None]):
    _TYPE = type(None)


none_validator = NoneValidator()


class OptionalValidator(Validator[Any, Optional[A]]):
    """
    We have a value for a key, but it can be null (None)
    """

    __slots__ = ("validator",)
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[Any, A]) -> None:
        self.validator = UnionValidatorAny(none_validator, validator)

    async def validate_async(self, val: Any) -> ValidationResult[Optional[A]]:
        return await self.validator.validate_async(val)

    def __call__(self, val: Any) -> ValidationResult[Optional[A]]:
        return self.validator(val)
