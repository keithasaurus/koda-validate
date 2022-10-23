from dataclasses import dataclass

from koda import Ok

from koda_validate.dictionary import dict_validator, key
from koda_validate.generic import Min
from koda_validate.integer import IntValidator
from koda_validate.string import MinLength, StringValidator


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,  # <- destination of data if valid
    key("name", StringValidator(MinLength(1))),  # <- first key
    key("age", IntValidator(Min(0))),  # <- second key...
)

# note that `match` statements can be used in python >= 3.10
result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Ok):
    print(f"{result.val.name} is {result.val.age} years old")
else:
    print(result.val)
