import math
from dataclasses import dataclass

from koda import Err, Ok

from koda_validate.typedefs import JSONValue, Predicate
from koda_validate.validators.validators import FloatValidator


@dataclass
class IsClose(Predicate[float, JSONValue]):
    compare_to: float
    tolerance: float

    def is_valid(self, val: float) -> bool:
        return math.isclose(self.compare_to, val, abs_tol=self.tolerance)

    def err_message(self, val: float) -> JSONValue:
        return f"expected a value within {self.tolerance} of {self.compare_to}"


# let's use it
close_to_validator = FloatValidator(IsClose(0.05, 0.02))
a = 0.06
assert close_to_validator(a) == Ok(a)
assert close_to_validator(0.01) == Err(["expected a value within 0.02 of 0.05"])
