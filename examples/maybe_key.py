from dataclasses import dataclass

from koda import Just, Maybe, Ok, nothing

from koda_validate import DictValidator, IntValidator, StringValidator
from koda_validate.dictionary import KeyNotRequired


@dataclass
class Person:
    name: str
    age: Maybe[int]


person_validator = DictValidator(
    into=Person,
    keys=(("name", StringValidator()), ("age", KeyNotRequired(IntValidator()))),
)
assert person_validator({"name": "Bob"}) == Ok(Person("Bob", nothing))
assert person_validator({"name": "Bob", "age": 42}) == Ok(Person("Bob", Just(42)))
