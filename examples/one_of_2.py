from koda_validate import *
from koda_validate.union import UnionValidator

string_or_list_string_validator = UnionValidator.typed(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Valid("ok")
assert string_or_list_string_validator(["list", "of", "strings"]) == Valid(
    ["list", "of", "strings"]
)
