"""
We should replace Tuple2Validator and Tuple3Validator
with a generic TupleValidator... (2 and 3 can still use the new one
under the hood, if needed)
"""

from typing import Any, Callable, Dict, Final, Optional, Tuple

from koda import Err, Result

from koda_validate._cruft import _typed_tuple
from koda_validate._generics import A, B, C
from koda_validate._validate_and_map import validate_and_map
from koda_validate.typedefs import Serializable, Validator
from koda_validate.utils import OBJECT_ERRORS_FIELD


def _tuple_to_dict_errors(errs: Tuple[Serializable, ...]) -> Dict[str, Serializable]:
    return {str(i): err for i, err in enumerate(errs)}


EXPECTED_TUPLE_TWO_ERROR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected list or tuple of length 2"]}
)

EXPECTED_TUPLE_THREE_ERROR: Final[Err[Serializable]] = Err(
    {OBJECT_ERRORS_FIELD: ["expected list or tuple of length 3"]}
)


# todo: auto-generate
class Tuple2Validator(Validator[Any, Tuple[A, B], Serializable]):
    required_length: int = 2

    __match_args__ = ("slot1_validator", "slot2_validator", "tuple_validator")
    __slots__ = __match_args__

    def __init__(
        self,
        slot1_validator: Validator[Any, A, Serializable],
        slot2_validator: Validator[Any, B, Serializable],
        tuple_validator: Optional[
            Callable[[Tuple[A, B]], Result[Tuple[A, B], Serializable]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Result[Tuple[A, B], Tuple[Serializable, ...]] = validate_and_map(
                _typed_tuple,
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
            )

            if not result.is_ok:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_TWO_ERROR

    async def validate_async(self, data: Any) -> Result[Tuple[A, B], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Result[Tuple[A, B], Tuple[Serializable, ...]] = validate_and_map(
                _typed_tuple,
                await self.slot1_validator.validate_async(data[0]),
                await self.slot2_validator.validate_async(data[1]),
            )

            if not result.is_ok:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_TWO_ERROR


class Tuple3Validator(Validator[Any, Tuple[A, B, C], Serializable]):
    required_length: int = 3
    __match_args__ = (
        "slot1_validator",
        "slot2_validator",
        "slot3_validator",
        "tuple_validator",
    )
    __slots__ = __match_args__

    def __init__(
        self,
        slot1_validator: Validator[Any, A, Serializable],
        slot2_validator: Validator[Any, B, Serializable],
        slot3_validator: Validator[Any, C, Serializable],
        tuple_validator: Optional[
            Callable[[Tuple[A, B, C]], Result[Tuple[A, B, C], Serializable]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B, C], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Result[Tuple[A, B, C], Tuple[Serializable, ...]] = validate_and_map(
                _typed_tuple,
                self.slot1_validator(data[0]),
                self.slot2_validator(data[1]),
                self.slot3_validator(data[2]),
            )

            if not result.is_ok:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_THREE_ERROR

    async def validate_async(self, data: Any) -> Result[Tuple[A, B, C], Serializable]:
        if isinstance(data, (list, tuple)) and len(data) == self.required_length:
            result: Result[Tuple[A, B, C], Tuple[Serializable, ...]] = validate_and_map(
                _typed_tuple,
                await self.slot1_validator.validate_async(data[0]),
                await self.slot2_validator.validate_async(data[1]),
                await self.slot3_validator.validate_async(data[2]),
            )

            if not result.is_ok:
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return EXPECTED_TUPLE_THREE_ERROR
