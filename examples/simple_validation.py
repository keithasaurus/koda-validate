from koda_validate import ExactValidator, MinLength, StringValidator
from koda_validate.typedefs import Invalid, Valid

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Valid("good")
assert min_length_3_validator("bad") == Invalid(["minimum allowed length is 4"])

exactly_5_validator = ExactValidator(5)

assert exactly_5_validator(5) == Valid(5)
assert exactly_5_validator("hmm") == Invalid(["expected exactly 5 (int)"])
