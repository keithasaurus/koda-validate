from koda_validate import *
from koda_validate.union import UnionValidatorIndexed

string_or_list_string_validator = UnionValidatorIndexed.typed(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Valid((0, "ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Valid(
    (1, ["list", "of", "strings"])
)
