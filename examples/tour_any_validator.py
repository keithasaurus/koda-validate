from koda_validate import *

assert always_valid(123) == Valid(123)
assert always_valid("abc") == Valid("abc")
