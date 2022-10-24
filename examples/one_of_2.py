from koda import First, Ok, Second

from koda_validate import ListValidator, OneOf2, StringValidator

string_or_list_string_validator = OneOf2(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Ok(First("ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Ok(
    Second(["list", "of", "strings"])
)
