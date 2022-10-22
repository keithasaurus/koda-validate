from dataclasses import dataclass

from koda import Err, Ok

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

# for python >= 3.10 only. Use `if isinstance(...)` with python < 3.10
match person_validator({"name": "John Doe", "age": 30}):
    case Ok(Person(name, age)):
        print(f"{name} is {age} years old")
    case Err(errs):
        print(errs)
