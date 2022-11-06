from typing import Any, Final, Literal, Optional, Tuple

from koda._generics import A

from koda_validate._internals import _variant_errors
from koda_validate.typedefs import (
    Serializable,
    Validator,
    _ResultTuple,
    _ToTupleValidator,
)

TRUE_NONE: Final[Tuple[Literal[True], None]] = True, None
TRUE_NONE_OPTIONAL: Final[Tuple[Literal[True], Optional[Any]]] = True, None


class OptionalValidator(_ToTupleValidator[Any, Optional[A], Serializable]):
    """
    We have a value for a key, but it can be null (None)
    """

    __slots__ = ("validator",)
    __match_args__ = ("validator",)

    def __init__(self, validator: Validator[Any, A, Serializable]) -> None:
        self.validator = validator

    def validate_to_tuple(self, val: Any) -> _ResultTuple[Optional[A], Serializable]:
        if val is None:
            return TRUE_NONE_OPTIONAL
        else:
            if isinstance(self.validator, _ToTupleValidator):
                succeeded, new_value = self.validator.validate_to_tuple(val)

            else:
                result = self.validator(val)
                if result.is_ok:
                    succeeded, new_value = True, result.val
                else:
                    succeeded, new_value = False, result.val

            if succeeded:
                return True, new_value
            else:
                return False, _variant_errors(["must be None"], new_value)

    async def validate_to_tuple_async(
        self, val: Any
    ) -> _ResultTuple[Optional[A], Serializable]:
        if val is None:
            return TRUE_NONE_OPTIONAL
        else:
            if isinstance(self.validator, _ToTupleValidator):
                succeeded, new_value = await self.validator.validate_to_tuple_async(val)

            else:
                result = await self.validator.validate_async(val)
                if result.is_ok:
                    succeeded, new_value = True, result.val
                else:
                    succeeded, new_value = False, result.val

            if succeeded:
                return True, new_value
            else:
                return False, _variant_errors(["must be None"], new_value)


EXPECTED_NONE: Final[Tuple[Literal[False], Serializable]] = False, ["expected None"]


class NoneValidator(_ToTupleValidator[Any, None, Serializable]):
    def validate_to_tuple(self, val: Any) -> _ResultTuple[None, Serializable]:
        if val is None:
            return TRUE_NONE
        else:
            return EXPECTED_NONE

    async def validate_to_tuple_async(self, val: Any) -> _ResultTuple[None, Serializable]:
        return self.validate_to_tuple(val)


none_validator = NoneValidator()
