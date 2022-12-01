from koda_validate import *
from koda_validate.base import InvalidKeyVal, InvalidMap, InvalidType

str_validator = StringValidator()
int_validator = IntValidator()
str_to_int_validator = MapValidator(key=str_validator, value=int_validator)

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)

assert str_to_int_validator({3.14: "pi!"}) == Invalid(
    str_to_int_validator,
    InvalidMap(
        {
            3.14: InvalidKeyVal(
                Invalid(str_validator, InvalidType(str)),
                Invalid(int_validator, InvalidType(int)),
            )
        },
    ),
)
