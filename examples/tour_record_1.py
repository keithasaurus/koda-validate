from dataclasses import dataclass

from koda import Just, Maybe

from koda_validate import *


@dataclass
class Person:
    name: str
    age: Maybe[int]


person_validator = RecordValidator(
    into=Person,
    keys=(
        ("full name", StringValidator()),
        ("age", KeyNotRequired(IntValidator())),
    ),
)

match person_validator({"full name": "John Doe", "age": 30}):
    case Valid(person):
        match person.age:
            case Just(age):
                age_message = f"{age} years old"
            case nothing:
                age_message = "ageless"
        print(f"{person.name} is {age_message}")
    case Invalid(_, errs):
        print(errs)
