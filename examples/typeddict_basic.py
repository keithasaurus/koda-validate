from typing import TypedDict, List

from koda_validate import TypedDictValidator


class Person(TypedDict):
    name: str
    hobbies: List[str]


person_validator = TypedDictValidator(Person)
person_validator({"name": "Bob", "hobbies": ["eating", "coding", "sleeping"]})
# > Valid({'name': 'Bob', 'hobbies': ['eating', 'coding', 'sleeping']})
