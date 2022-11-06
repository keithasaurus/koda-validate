from koda_validate import IntValidator, OptionalValidator
from koda_validate.typedefs import Ok

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Ok(5)
assert optional_int_validator(None) == Ok(None)
