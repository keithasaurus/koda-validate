from typing import Any

from koda import Just, Maybe, nothing

from koda_validate import Validator
from koda_validate._generics import A
from koda_validate.base import _ResultTupleUnsafe, _ToTupleValidatorUnsafe


class MaybeValidator(_ToTupleValidatorUnsafe[Any, Maybe[A]]):
    def __init__(self, validator: Validator[Any, A]):
        self.validator = validator

    def validate_to_tuple(self, val: Any) -> _ResultTupleUnsafe:
        if val is nothing:
            return True, nothing
        elif type(val) is Just:
            if isinstance(self.validator, _ToTupleValidatorUnsafe):
                succeeded, new_val = self.validator.validate_to_tuple(val.val)
                if succeeded:
                    return True, Just(new_val)
                else:
                    return False, new_val
            else:
                result = self.validator(val.val)
                if result.is_valid:
                    return True, Just(result.val)
                else:
                    return False, result.val
        else:
            return False, "expected a Maybe instance"

    async def validate_to_tuple_async(self, val: Any) -> _ResultTupleUnsafe:
        if val is nothing:
            return True, nothing
        elif type(val) is Just:
            if isinstance(self.validator, _ToTupleValidatorUnsafe):
                succeeded, new_val = await self.validator.validate_to_tuple_async(val.val)
                if succeeded:
                    return True, Just(new_val)
                else:
                    return False, new_val
            else:
                result = await self.validator.validate_async(val.val)
                if result.is_valid:
                    return True, Just(result.val)
                else:
                    return False, result.val
        else:
            return False, "expected a Maybe instance"
