from dataclasses import dataclass

from koda import Just, Maybe, Ok, nothing

from koda_validate import IntValidator, StringValidator, dict_validator, key, maybe_key


@dataclass
class Person:
    name: str
    age: Maybe[str]


person_validator = dict_validator(
    Person, key("name", StringValidator()), maybe_key("age", IntValidator())
)
assert person_validator({"name": "Bob"}) == Ok(Person("Bob", nothing))
assert person_validator({"name": "Bob", "age": 42}) == Ok(Person("Bob", Just(42)))
