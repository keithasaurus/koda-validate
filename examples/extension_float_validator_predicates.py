from dataclasses import dataclass
from typing import Any, Optional

from koda_validate import *


@dataclass
class SimpleFloatValidator2(Validator[Any, float, Serializable]):
    predicate: Optional[Predicate[float, Serializable]] = None

    def __call__(self, val: Any) -> Validated[float, Serializable]:
        if isinstance(val, float):
            if self.predicate:
                return self.predicate(val)
            else:
                return Valid(val)
        else:
            return Invalid(["expected a float"])


@dataclass
class Range(Predicate[float, Serializable]):
    minimum: float
    maximum: float

    def is_valid(self, val: float) -> bool:
        return self.minimum <= val <= self.maximum

    def err(self, val: float) -> Serializable:
        return f"expected a value in the range of {self.minimum} and {self.maximum}"


range_validator = SimpleFloatValidator2(Range(0.5, 1.0))
test_val = 0.7

assert range_validator(test_val) == Valid(test_val)

assert range_validator(0.01) == Invalid("expected a value in the range of 0.5 and 1.0")


@dataclass
class SimpleFloatValidator3(Validator[Any, float, Serializable]):
    predicate: Optional[Predicate[float, Serializable]] = None
    preprocessor: Optional[Processor[float]] = None

    def __call__(self, val: Any) -> Validated[float, Serializable]:
        if isinstance(val, float):
            if self.preprocessor:
                val = self.preprocessor(val)

            if self.predicate:
                return self.predicate(val)
            else:
                return Valid(val)
        else:
            return Invalid(["expected a float"])


class AbsValue(Processor[float]):
    def __call__(self, val: float) -> float:
        return abs(val)


range_validator_2 = SimpleFloatValidator3(
    predicate=Range(0.5, 1.0), preprocessor=AbsValue()
)

test_val = -0.7

assert range_validator_2(test_val) == Valid(abs(test_val))

assert range_validator_2(-0.01) == Invalid("expected a value in the range of 0.5 and 1.0")
