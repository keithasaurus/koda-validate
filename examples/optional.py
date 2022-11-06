from koda_validate import IntValidator, OptionalValidator
from koda_validate.validated import Valid

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Valid(5)
assert optional_int_validator(None) == Valid(None)
