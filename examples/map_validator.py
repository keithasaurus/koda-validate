from koda_validate import *
from koda_validate import MapErr, TypeErr
from koda_validate.errors import KeyValErrs

str_validator = StringValidator()
int_validator = IntValidator()
str_to_int_validator = MapValidator(key=str_validator, value=int_validator)

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)

assert str_to_int_validator({3.14: "pi!"}) == Invalid(
    MapErr(
        {
            3.14: KeyValErrs(
                Invalid(
                    TypeErr(str),
                    3.14,
                    str_validator,
                ),
                Invalid(
                    TypeErr(int),
                    "pi!",
                    int_validator,
                ),
            )
        },
    ),
    {3.14: "pi!"},
    str_to_int_validator,
)
