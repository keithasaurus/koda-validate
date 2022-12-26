from pprint import pprint
from typing import TypedDict

from koda_validate import TypedDictValidator, to_serializable_errs


class Person(TypedDict):
    name: str
    age: int


validator = TypedDictValidator(Person)

result = validator({"age": False})

to_serializable_errs(result)
# > {'age': ['expected an integer'], 'name': ['key missing']}

# you can write something like
# to_some_other_error_format(result)
