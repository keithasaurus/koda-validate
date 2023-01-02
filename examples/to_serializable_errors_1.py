from koda_validate import *

validator = StringValidator()

result = validator(123)
assert isinstance(result, Invalid)

print(to_serializable_errs(result))
