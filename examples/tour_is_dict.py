from koda_validate import *

assert is_dict_validator({}) == Valid({})
assert is_dict_validator(None) == Invalid({"__container__": ["expected a dictionary"]})
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Valid({"a": 1, "b": 2, 5: "xyz"})
