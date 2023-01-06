from koda_validate import IntValidator, NTupleValidator, StringValidator, Valid

string_int_validator = NTupleValidator.typed(fields=(StringValidator(), IntValidator()))

assert string_int_validator(("ok", 100)) == Valid(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Valid(("ok", 100))
