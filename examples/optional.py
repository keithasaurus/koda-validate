from koda import Ok

from koda_validate.integer import IntValidator
from koda_validate.none import OptionalValidator

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Ok(5)
assert optional_int_validator(None) == Ok(None)
