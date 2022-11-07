from koda_validate import *

assert any_validator(123) == Valid(123)
assert any_validator("abc") == Valid("abc")
