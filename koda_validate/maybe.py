from typing import Any

from koda import Just, Maybe, nothing

from koda_validate._generics import A
from koda_validate._internal import (
    _ResultTuple,
    _ToTupleValidator,
    _wrap_async_validator,
    _wrap_sync_validator,
)
from koda_validate.base import Validator
from koda_validate.errors import ContainerErr, TypeErr
from koda_validate.valid import Invalid


class MaybeValidator(_ToTupleValidator[Maybe[A]]):
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[A]):
        self.validator = validator
        self._validator_sync = _wrap_sync_validator(self.validator)
        self._validator_async = _wrap_async_validator(self.validator)

    async def _validate_to_tuple_async(self, val: Any) -> _ResultTuple[Maybe[A]]:
        if val is nothing:
            return True, nothing
        elif type(val) is Just:
            result = await self._validator_async(val.val)
            if result[0]:
                return True, Just(result[1])
            else:
                return False, Invalid(ContainerErr(result[1]), val, self)
        else:
            return False, Invalid(TypeErr(Maybe[Any]), val, self)  # type: ignore[misc]

    def _validate_to_tuple(self, val: Any) -> _ResultTuple[Maybe[A]]:
        if val is nothing:
            return True, nothing
        elif type(val) is Just:
            result = self._validator_sync(val.val)
            if result[0]:
                return True, Just(result[1])
            else:
                return False, Invalid(ContainerErr(result[1]), val, self)
        else:
            return False, Invalid(TypeErr(Maybe[Any]), val, self)  # type: ignore[misc]

    def __eq__(self, other: Any) -> bool:
        return type(self) == type(other) and self.validator == other.validator

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.validator)})"
