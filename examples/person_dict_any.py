from koda_validate import *

person_validator = DictValidatorAny(
    {
        "name": StringValidator(),
        "age": IntValidator(),
    }
)

result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Valid):
    print(f"{result.val['name']} is {result.val['age']} years old")
else:
    print(result.val)

# prints: "John Doe is 30 years old"
