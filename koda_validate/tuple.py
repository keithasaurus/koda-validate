from typing import Any, Callable, Dict, Optional, Tuple

from koda import Err, Result

from koda_validate._cruft import _typed_tuple
from koda_validate._generics import A, B, C
from koda_validate.typedefs import Serializable, Validator
from koda_validate.utils import OBJECT_ERRORS_FIELD
from koda_validate.validate_and_map import validate_and_map


def _tuple_to_dict_errors(errs: Tuple[Serializable, ...]) -> Dict[str, Serializable]:
    return {str(i): err for i, err in enumerate(errs)}


# todo: auto-generate
class Tuple2Validator(Validator[Any, Tuple[A, B], Serializable]):
    __slots__ = ("slot1_validator", "slot2_validator", "tuple_validator")
    __match_args__ = ("slot1_validator", "slot2_validator", "tuple_validator")

    required_length: int = 2

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, Serializable]],
        slot2_validator: Callable[[Any], Result[B, Serializable]],
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

            if isinstance(result, Err):
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return Err(
                {
                    OBJECT_ERRORS_FIELD: [
                        f"expected list or tuple of length {self.required_length}"
                    ]
                }
            )


class Tuple3Validator(Validator[Any, Tuple[A, B, C], Serializable]):
    __slots__ = (
        "slot1_validator",
        "slot2_validator",
        "slot3_validator",
        "tuple_validator",
    )
    __match_args__ = (
        "slot1_validator",
        "slot2_validator",
        "slot3_validator",
        "tuple_validator",
    )

    required_length: int = 3

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, Serializable]],
        slot2_validator: Callable[[Any], Result[B, Serializable]],
        slot3_validator: Callable[[Any], Result[C, Serializable]],
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

            if isinstance(result, Err):
                return result.map_err(_tuple_to_dict_errors)
            else:
                if self.tuple_validator is None:
                    return result
                else:
                    return result.flat_map(self.tuple_validator)
        else:
            return Err(
                {
                    OBJECT_ERRORS_FIELD: [
                        f"expected list or tuple of length {self.required_length}"
                    ]
                }
            )
