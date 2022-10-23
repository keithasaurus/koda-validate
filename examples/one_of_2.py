from koda import First, Ok, Second

from koda_validate.list import ListValidator
from koda_validate.one_of import OneOf2
from koda_validate.string import StringValidator

string_or_list_string_validator = OneOf2(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Ok(First("ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Ok(
    Second(["list", "of", "strings"])
)
