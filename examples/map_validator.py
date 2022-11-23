from koda_validate import *
from koda_validate.base import InvalidKeyVal, InvalidMap, InvalidType

str_to_int_validator = MapValidator(key=StringValidator(), value=IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)

assert str_to_int_validator({3.14: "pi!"}) == Invalid(
    InvalidMap(
        {
            3.14: InvalidKeyVal(
                InvalidType(str, "expected a string"),
                InvalidType(int, "expected an integer"),
            )
        }
    )
)
