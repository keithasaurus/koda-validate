from dataclasses import dataclass
from typing import Any, Optional

from koda import Err, Just, Maybe, Ok, Result, nothing
from koda._generics import A

from koda_validate.typedefs import JSONValue, Validator
from koda_validate.utils import _variant_errors, expected


@dataclass(frozen=True)
class OptionalValidator(Validator[Any, Optional[A], JSONValue]):
    """
    We have a value for a key, but it can be null (None)
    """

    validator: Validator[Any, A, JSONValue]

    def __call__(self, val: Optional[Any]) -> Result[Optional[A], JSONValue]:
        if val is None:
            return Ok(None)
        else:
            result: Result[A, JSONValue] = self.validator(val)
            if isinstance(result, Ok):
                return Ok(result.val)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )


class NoneValidator(Validator[Any, None, JSONValue]):
    def __call__(self, val: Any) -> Result[None, JSONValue]:
        if val is None:
            return Ok(val)
        else:
            return Err([expected("null")])


none_validator = NoneValidator()
