from typing import Any, ClassVar, Optional

from koda._generics import A

from koda_validate._internal import ResultTuple, _ToTupleValidator
from koda_validate.base import Invalid, TypeErr, ValidationResult, Validator
from koda_validate.union import UnionValidatorAny


class NoneValidator(_ToTupleValidator[None]):
    _instance: ClassVar[Optional["NoneValidator"]] = None

    def __new__(cls) -> "NoneValidator":
        """
        Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(NoneValidator, cls).__new__(cls)
        return cls._instance

    def validate_to_tuple(self, val: Any) -> ResultTuple[None]:
        if val is None:
            return True, None
        else:
            return False, Invalid(self, val, TypeErr(type(None)))

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[None]:
        return self.validate_to_tuple(val)

    def __repr__(self) -> str:
        return "NoneValidator()"


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
