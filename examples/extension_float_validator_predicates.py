from dataclasses import dataclass
from typing import Any, Optional

from koda_validate import *
from koda_validate.base import PredicateErrs, TypeErr, ValidationResult


@dataclass
class SimpleFloatValidator2(Validator[float]):
    predicate: Optional[Predicate[float]] = None

    def __call__(self, val: Any) -> ValidationResult[float]:
        if isinstance(val, float):
            if self.predicate:
                return (
                    Valid(val)
                    if self.predicate(val)
                    else Invalid(self, val, PredicateErrs([self.predicate]))
                )
            else:
                return Valid(val)
        else:
            return Invalid(self, val, TypeErr(float))


@dataclass
class Range(Predicate[float]):
    minimum: float
    maximum: float

    def __call__(self, val: float) -> bool:
        return self.minimum <= val <= self.maximum


range_validator = SimpleFloatValidator2(Range(0.5, 1.0))
test_val = 0.7

assert range_validator(test_val) == Valid(test_val)

assert range_validator(0.01) == Invalid(
    range_validator, 0.01, PredicateErrs([Range(0.5, 1.0)])
)


@dataclass
class SimpleFloatValidator3(Validator[float]):
    predicate: Optional[Predicate[float]] = None
    preprocessor: Optional[Processor[float]] = None

    def __call__(self, val: Any) -> ValidationResult[float]:
        if isinstance(val, float):
            if self.preprocessor:
                val = self.preprocessor(val)

            if self.predicate:
                return (
                    Valid(val)
                    if self.predicate(val)
                    else Invalid(self, val, PredicateErrs([self.predicate]))
                )
            else:
                return Valid(val)
        else:
            return Invalid(self, val, TypeErr(float))


class AbsValue(Processor[float]):
    def __call__(self, val: float) -> float:
        return abs(val)


range_validator_2 = SimpleFloatValidator3(
    predicate=Range(0.5, 1.0), preprocessor=AbsValue()
)

test_val = -0.7

assert range_validator_2(test_val) == Valid(abs(test_val))

assert range_validator_2(-0.01) == Invalid(
    range_validator_2, 0.01, PredicateErrs([Range(0.5, 1.0)])
)
