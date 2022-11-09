from koda_validate import *

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Valid(5)
assert optional_int_validator(None) == Valid(None)
