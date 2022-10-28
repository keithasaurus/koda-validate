from dataclasses import dataclass
from typing import Any, Optional

from koda import Err, Ok, Result
from koda._generics import A

from koda_validate.typedefs import Serializable, Validator
from koda_validate.utils import _variant_errors


@dataclass(frozen=True)
class OptionalValidator(Validator[Any, Optional[A], Serializable]):
    """
    We have a value for a key, but it can be null (None)
    """

    validator: Validator[Any, A, Serializable]

    def __call__(self, val: Optional[Any]) -> Result[Optional[A], Serializable]:
        if val is None:
            return Ok(None)
        else:
            result: Result[A, Serializable] = self.validator(val)
            if isinstance(result, Ok):
                return Ok(result.val)
            else:
                return result.map_err(
                    lambda errs: _variant_errors(["must be None"], errs)
                )


class NoneValidator(Validator[Any, None, Serializable]):
    def __call__(self, val: Any) -> Result[None, Serializable]:
        if val is None:
            return Ok(val)
        else:
            return Err([f"expected null"])


none_validator = NoneValidator()
