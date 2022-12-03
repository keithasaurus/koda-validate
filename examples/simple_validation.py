from koda_validate import EqualsValidator, Invalid, MinLength, StringValidator, Valid
from koda_validate.base import PredicateErrs, TypeErr

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Valid("good")
assert min_length_3_validator("bad") == Invalid(
    min_length_3_validator, "bad", PredicateErrs([MinLength(4)])
)

exactly_5_validator = EqualsValidator(5)

assert exactly_5_validator(5) == Valid(5)
assert exactly_5_validator("hmm") == Invalid(exactly_5_validator, "hmm", TypeErr(int))
