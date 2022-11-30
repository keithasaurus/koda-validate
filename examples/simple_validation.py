from koda_validate import EqualsValidator, Invalid, MinLength, StringValidator, Valid
from koda_validate.base import InvalidPredicates, InvalidType

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Valid("good")
assert min_length_3_validator("bad") == Invalid(
    InvalidPredicates(min_length_3_validator, [MinLength(4)])
)

exactly_5_validator = EqualsValidator(5)

assert exactly_5_validator(5) == Valid(5)
assert exactly_5_validator("hmm") == Invalid(InvalidType(exactly_5_validator, int))
