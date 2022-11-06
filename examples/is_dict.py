from koda_validate.dictionary import is_dict_validator
from koda_validate.validated import Invalid, Valid

assert is_dict_validator({}) == Valid({})
assert is_dict_validator(None) == Invalid({"__container__": ["expected a dictionary"]})
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Valid({"a": 1, "b": 2, 5: "xyz"})
