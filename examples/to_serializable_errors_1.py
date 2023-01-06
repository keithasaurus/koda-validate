from koda_validate import *
from koda_validate.serialization import to_serializable_errs

validator = StringValidator()

result = validator(123)
assert isinstance(result, Invalid)

print(to_serializable_errs(result))
