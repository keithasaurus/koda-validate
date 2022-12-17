from koda_validate import (
    EqualsValidator,
    Invalid,
    MinLength,
    PredicateErrs,
    StringValidator,
    TypeErr,
    Valid,
)

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Valid("good")
assert min_length_3_validator("bad") == Invalid(
    PredicateErrs([MinLength(4)]), "bad", min_length_3_validator
)

exactly_5_validator = EqualsValidator(5)

assert exactly_5_validator(5) == Valid(5)
assert exactly_5_validator("hmm") == Invalid(TypeErr(int), "hmm", exactly_5_validator)
