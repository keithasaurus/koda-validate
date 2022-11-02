from dataclasses import dataclass

from koda import Ok

from koda_validate import *


@dataclass
class Person:
    name: str
    age: int


person_validator = DictValidator(
    into=Person,
    keys=(
        ("name", StringValidator()),
        ("age", IntValidator()),
    ),
)

result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Ok):
    print(f"{result.val.name} is {result.val.age} years old")
else:
    print(result.val)

people_validator = ListValidator(person_validator)


@dataclass
class Group:
    name: str
    people: list[Person]


group_validator = DictValidator(
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

assert group_validator(data) == Ok(
    Group(
        name="Arrested Development Characters",
        people=[
            Person(name="George Bluth", age=70),
            Person(name="Michael Bluth", age=35),
        ],
    )
)
