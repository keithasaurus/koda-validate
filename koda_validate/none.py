from typing import Any, ClassVar, Optional

from koda_validate._generics import A
from koda_validate._internal import (
    _ResultTuple,
    _ToTupleValidator,
    _union_validator,
    _union_validator_async,
)
from koda_validate.base import Validator
from koda_validate.errors import TypeErr
from koda_validate.valid import Invalid


class NoneValidator(_ToTupleValidator[None]):
    _instance: ClassVar[Optional["NoneValidator"]] = None

    def __new__(cls) -> "NoneValidator":
        # make a singleton
        if cls._instance is None:
            cls._instance = super(NoneValidator, cls).__new__(cls)
        return cls._instance

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[None]:
        if val is None:
            return True, None
        else:
            return False, Invalid(TypeErr(type(None)), val, self)

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[None]:
        return self._validate_to_tuple(val)

    def __repr__(self) -> str:
        return "NoneValidator()"


none_validator = NoneValidator()


class OptionalValidator(_ToTupleValidator[Optional[A]]):
    """
    We have a value for a key, but it can be null (None)
    """

    __match_args__ = ("non_none_validator",)

    def __init__(self, validator: Validator[A]) -> None:
        self.non_none_validator = validator
        self.validators = (none_validator, validator)

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[Optional[A]]:
        return await _union_validator_async(self, self.validators, val)

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[Optional[A]]:
        return _union_validator(self, self.validators, val)

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)
            and other.non_none_validator == self.non_none_validator
        )

    def __repr__(self) -> str:
        return f"OptionalValidator({repr(self.non_none_validator)})"
