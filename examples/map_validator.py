from koda_validate import *

str_to_int_validator = MapValidator(key=StringValidator(), value=IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)
