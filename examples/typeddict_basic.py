from typing import TypedDict

from koda_validate import TypedDictValidator


class Person(TypedDict):
    name: str
    hobbies: list[str]


person_validator = TypedDictValidator(Person)
person_validator({"name": "Bob", "hobbies": ["eating", "coding", "sleeping"]})
# > Valid({'name': 'Bob', 'hobbies': ['eating', 'coding', 'sleeping']})
