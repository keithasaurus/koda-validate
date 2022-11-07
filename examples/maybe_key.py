from dataclasses import dataclass

from koda import Just, Maybe, nothing

from koda_validate import *


@dataclass
class Person:
    name: str
    age: Maybe[int]


person_validator = DictValidator(
    into=Person,
    keys=(("name", StringValidator()), ("age", KeyNotRequired(IntValidator()))),
)
assert person_validator({"name": "Bob"}) == Valid(Person("Bob", nothing))
assert person_validator({"name": "Bob", "age": 42}) == Valid(Person("Bob", Just(42)))
