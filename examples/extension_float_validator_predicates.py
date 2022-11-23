from dataclasses import dataclass
from typing import Any, Optional

from koda_validate import *
from koda_validate.base import TypeErr, ValidationErr


@dataclass
class SimpleFloatValidator2(Validator[Any, float]):
    predicate: Optional[Predicate[float]] = None

    def __call__(self, val: Any) -> Validated[float, ValidationErr]:
        if isinstance(val, float):
            if self.predicate:
                return Valid(val) if self.predicate(val) else Invalid([self.predicate])
            else:
                return Valid(val)
        else:
            return Invalid(TypeErr(float, "expected a float"))


@dataclass
class Range(Predicate[float]):
    minimum: float
    maximum: float

    def __post_init__(self) -> None:
        self.err_message = (
            f"expected a value in the range of {self.minimum} and {self.maximum}"
        )

    def __call__(self, val: float) -> bool:
        return self.minimum <= val <= self.maximum


range_validator = SimpleFloatValidator2(Range(0.5, 1.0))
test_val = 0.7

assert range_validator(test_val) == Valid(test_val)

assert range_validator(0.01) == Invalid(Range(0.5, 1.0))


@dataclass
class SimpleFloatValidator3(Validator[Any, float]):
    predicate: Optional[Predicate[float]] = None
    preprocessor: Optional[Processor[float]] = None

    def __call__(self, val: Any) -> Validated[float, ValidationErr]:
        if isinstance(val, float):
            if self.preprocessor:
                val = self.preprocessor(val)

            if self.predicate:
                return Valid(val) if self.predicate(val) else Invalid([self.predicate])
            else:
                return Valid(val)
        else:
            return Invalid(TypeErr(float, "expected a float"))


class AbsValue(Processor[float]):
    def __call__(self, val: float) -> float:
        return abs(val)


range_validator_2 = SimpleFloatValidator3(
    predicate=Range(0.5, 1.0), preprocessor=AbsValue()
)

test_val = -0.7

assert range_validator_2(test_val) == Valid(abs(test_val))

assert range_validator_2(-0.01) == Invalid("expected a value in the range of 0.5 and 1.0")
