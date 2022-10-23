from koda import Ok

from koda_validate.integer import IntValidator
from koda_validate.string import StringValidator
from koda_validate.tuple import Tuple2Validator

string_int_validator = Tuple2Validator(StringValidator(), IntValidator())

assert string_int_validator(("ok", 100)) == Ok(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Ok(("ok", 100))
