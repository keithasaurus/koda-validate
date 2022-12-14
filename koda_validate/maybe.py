from typing import Any

from koda import Just, Maybe, nothing

from koda_validate._generics import A
from koda_validate._internal import (
    ResultTuple,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import ContainerErr, Invalid, TypeErr, Validator


class MaybeValidator(_ToTupleValidator[Maybe[A]]):
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[A]):
        self.validator = validator
        self._validator_sync = _wrap_sync_validator(self.validator)
        self._validator_async = _wrap_async_validator(self.validator)

    async def validate_to_tuple_async(self, val: Any) -> ResultTuple[Maybe[A]]:
        if val is nothing:
            return True, nothing
        elif type(val) is Just:
            success, new_val = await self._validator_async(val.val)
            if success:
                return True, Just(new_val)
            else:
                return False, Invalid(ContainerErr(new_val), val, self)
        else:
            return False, Invalid(TypeErr(Maybe), val, self)

    def validate_to_tuple(self, val: Any) -> ResultTuple[Maybe[A]]:
        if val is nothing:
            return True, nothing
        elif type(val) is Just:
            success, new_val = self._validator_sync(val.val)
            if success:
                return True, Just(new_val)
            else:
                return False, Invalid(ContainerErr(new_val), val, self)
        else:
            return False, Invalid(TypeErr(Maybe), val, self)

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other) and self.validator == other.validator

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.validator)})"
