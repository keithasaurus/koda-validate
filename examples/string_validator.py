from koda_validate import *

string_validator = StringValidator(MinLength(5))

string_validator("hello world")
# > Valid('hello world')

string_validator(5)
# > Invalid(...)
