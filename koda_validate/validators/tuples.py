from typing import Any, Callable, Dict, Optional, Tuple

from koda import Err, Result

from koda_validate._cruft import _typed_tuple
from koda_validate._generics import A, B, C
from koda_validate.typedefs import JSONValue, Validator
from koda_validate.utils import expected
from koda_validate.validators.validate_and_map import validate_and_map


def _tuple_to_dict_errors(errs: Tuple[JSONValue, ...]) -> Dict[str, JSONValue]:
    return {str(i): err for i, err in enumerate(errs)}


# todo: auto-generate
class Tuple2Validator(Validator[Any, Tuple[A, B], JSONValue]):
    required_length: int = 2

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, JSONValue]],
        slot2_validator: Callable[[Any], Result[B, JSONValue]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B]], Result[Tuple[A, B], JSONValue]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B], JSONValue]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B], Tuple[JSONValue, ...]] = validate_and_map(
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
                    "__container__": [
                        expected(f"list or tuple of length {self.required_length}")
                    ]
                }
            )


class Tuple3Validator(Validator[Any, Tuple[A, B, C], JSONValue]):
    required_length: int = 3

    def __init__(
        self,
        slot1_validator: Callable[[Any], Result[A, JSONValue]],
        slot2_validator: Callable[[Any], Result[B, JSONValue]],
        slot3_validator: Callable[[Any], Result[C, JSONValue]],
        tuple_validator: Optional[
            Callable[[Tuple[A, B, C]], Result[Tuple[A, B, C], JSONValue]]
        ] = None,
    ) -> None:
        self.slot1_validator = slot1_validator
        self.slot2_validator = slot2_validator
        self.slot3_validator = slot3_validator
        self.tuple_validator = tuple_validator

    def __call__(self, data: Any) -> Result[Tuple[A, B, C], JSONValue]:
        if isinstance(data, list) and len(data) == self.required_length:
            result: Result[Tuple[A, B, C], Tuple[JSONValue, ...]] = validate_and_map(
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
                    "__container__": [
                        expected(f"list or tuple of length {self.required_length}")
                    ]
                }
            )
