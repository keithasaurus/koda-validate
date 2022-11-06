from koda_validate import ExactValidator, MinLength, StringValidator
from koda_validate.typedefs import Err, Ok

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Ok("good")
assert min_length_3_validator("bad") == Err(["minimum allowed length is 4"])

exactly_5_validator = ExactValidator(5)

assert exactly_5_validator(5) == Ok(5)
assert exactly_5_validator("hmm") == Err(["expected exactly 5 (int)"])
