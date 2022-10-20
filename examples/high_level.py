from dataclasses import dataclass

from koda import Err, Ok

from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
    IntValidator,
    Minimum,
    MinLength,
    StringValidator,
    key,
)


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,  # <- if successful, we'll send the validated arguments here
    key("name", StringValidator(MinLength(1))),  # <- keys we're validating for
    key("age", IntValidator(Minimum(0))),
)

person_data = {"name": "John Doe", "age": 30}


match person_validator(person_data):
    case Ok(Person(name, age)):
        print(f"{name} is {age} years old")
    case Err(errs):
        print(errs)


@dataclass
class Employee:
    title: str
    person: Person


@dataclass
class Company:
    name: str
    industry: str
    employees: list[Employee]


# employee_validator = dict_validator(
#     Employee,
#     key("person", person_validator)
# )
