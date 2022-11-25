from koda_validate import *
from koda_validate.base import InvalidType

assert is_dict_validator({}) == Valid({})
assert is_dict_validator(None) == Invalid(InvalidType(dict, "expected a dictionary"))
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Valid({"a": 1, "b": 2, 5: "xyz"})
