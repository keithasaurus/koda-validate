from koda_validate import IntValidator, MapValidator, StringValidator
from koda_validate.validated import Valid

str_to_int_validator = MapValidator(StringValidator(), IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)
