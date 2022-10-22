from koda import Err, Ok

from koda_validate.list import ListValidator, MinItems
from koda_validate.string import MaxLength, MinLength, StringValidator

basic_string_validator = StringValidator()
assert basic_string_validator("neat") == Ok("neat")

string_length_validator = StringValidator(MinLength(2), MaxLength(5))

assert basic_string_validator("neat") == Ok("neat")
assert string_length_validator("") == Err(["minimum allowed length is 2"])


min_two_items_validator = ListValidator(StringValidator(MinLength(2)), MinItems(2))

assert min_two_items_validator(["ok", "cool", "wow"]) == Ok(["ok", "cool", "wow"])
assert min_two_items_validator([]) == Err(
    {"__container__": ["minimum allowed length is 2"]}
)
