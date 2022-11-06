from koda_validate.dictionary import is_dict_validator
from koda_validate.typedefs import Err, Ok

assert is_dict_validator({}) == Ok({})
assert is_dict_validator(None) == Err({"__container__": ["expected a dictionary"]})
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Ok({"a": 1, "b": 2, 5: "xyz"})
