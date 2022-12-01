from koda_validate import *
from koda_validate.base import PredicateErrs

int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

assert int_validator(12) == Valid(12)

assert int_validator(23) == Invalid(
    int_validator, PredicateErrs([Max(20), MultipleOf(4)])
)
