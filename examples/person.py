from dataclasses import dataclass
from typing import List
from koda_validate import *


@dataclass
class Person:
    name: str
    age: int


person_validator = RecordValidator(
    into=Person,
    keys=(
        ("name", StringValidator()),
        ("age", IntValidator()),
    ),
)

result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Valid):
    print(f"{result.val.name} is {result.val.age} years old")
else:
    print(result)

people_validator = ListValidator(person_validator)


@dataclass
class Group:
    name: str
    people: List[Person]


group_validator = RecordValidator(
    into=Group,
    keys=(
        ("name", StringValidator()),
        ("people", people_validator),
    ),
)

data = {
    "name": "Arrested Development Characters",
    "people": [{"name": "George Bluth", "age": 70}, {"name": "Michael Bluth", "age": 35}],
}

assert group_validator(data) == Valid(
    Group(
        name="Arrested Development Characters",
        people=[
            Person(name="George Bluth", age=70),
            Person(name="Michael Bluth", age=35),
        ],
    )
)
