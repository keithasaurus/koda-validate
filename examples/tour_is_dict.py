from koda_validate import *
from koda_validate.base import TypeErr

assert is_dict_validator({}) == Valid({})
assert is_dict_validator(None) == Invalid(is_dict_validator, TypeErr(dict))
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Valid({"a": 1, "b": 2, 5: "xyz"})
