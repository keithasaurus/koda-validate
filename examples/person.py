from dataclasses import dataclass

from koda import Ok

from koda_validate import *


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,  # <- destination of data if valid
    key("name", StringValidator()),  # <- first key
    key("age", IntValidator()),  # <- second key...
)

# note that `match` statements can be used in python >= 3.10
result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Ok):
    print(f"{result.val.name} is {result.val.age} years old")
else:
    print(result.val)
