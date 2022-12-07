import math
from dataclasses import dataclass

from koda_validate import *
from koda_validate.base import PredicateErrs


@dataclass
class IsClose(Predicate[float]):
    compare_to: float
    tolerance: float

    def __call__(self, val: float) -> bool:
        return math.isclose(self.compare_to, val, abs_tol=self.tolerance)


# let's use it
close_to_validator = FloatValidator(IsClose(0.05, 0.02))
a = 0.06
assert close_to_validator(a) == Valid(a)
assert close_to_validator(0.01) == Invalid(
    PredicateErrs([IsClose(0.05, 0.02)]), 0.01, close_to_validator
)
