from koda_validate import *

string_validator = StringValidator(MinLength(5))

string_validator("hello world")
# > Valid('hello world')

string_validator(5)
# > Invalid(...)

match string_validator("new string"):
    case Valid(valid_val):
        print(f"{valid_val} is valid!")
    case Invalid(_, err):
        print(f"got error: {err}")

# prints: "new string is valid"

if (result := string_validator("another string")).is_valid:
    print(f"{result.val} is valid!")
else:
    print(f"got error: {result}")

# prints: "another string is valid"
