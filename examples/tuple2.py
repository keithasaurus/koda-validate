from koda_validate import IntValidator, StringValidator, Tuple2Validator
from koda_validate.typedefs import Ok

string_int_validator = Tuple2Validator(StringValidator(), IntValidator())

assert string_int_validator(("ok", 100)) == Ok(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Ok(("ok", 100))
