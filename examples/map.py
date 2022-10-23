from koda import Ok

from koda_validate.dictionary import MapValidator
from koda_validate.integer import IntValidator
from koda_validate.string import StringValidator

str_to_int_validator = MapValidator(StringValidator(), IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Ok(
    {"a": 1, "b": 25, "xyz": 900}
)
