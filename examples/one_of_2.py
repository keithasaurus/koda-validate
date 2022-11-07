from koda import First, Second

from koda_validate import ListValidator, OneOf2, StringValidator, Valid

string_or_list_string_validator = OneOf2(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Valid(First("ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Valid(
    Second(["list", "of", "strings"])
)
