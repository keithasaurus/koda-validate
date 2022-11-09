from koda_validate import *

int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

assert int_validator(12) == Valid(12)

assert int_validator(23) == Invalid(
    ["maximum allowed value is 20", "expected multiple of 4"]
)
