from koda_validate import StringValidator

string_validator = StringValidator()

string_validator("hello world")
# > Ok('hello world')

string_validator(5)
# > Err(['expected a string'])
