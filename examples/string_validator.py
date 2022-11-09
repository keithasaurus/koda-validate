from koda_validate import *

string_validator = StringValidator()

string_validator("hello world")
# > Valid('hello world')

string_validator(5)
# > Invalid(['expected a string'])

match string_validator("new string"):
    case Valid(valid_val):
        print(f"{valid_val} is valid!")
    case Invalid(err):
        print(f"got error: {err}")

# prints: "new string is valid"

if (result := string_validator("another string")).is_valid:
    print(f"{result.val} is valid!")
else:
    print(f"got error: {result.val}")

# prints: "another string is valid"
