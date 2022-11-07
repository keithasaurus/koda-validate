from dataclasses import dataclass
from typing import List

from koda import Just, Maybe

from koda_validate import *


@dataclass
class Person:
    name: str
    age: Maybe[int]
    hobbies: List[str]


person_validator = RecordValidator(
    into=Person,
    keys=(
        (1, StringValidator()),
        (False, KeyNotRequired(IntValidator())),
        (("abc", 123), ListValidator(StringValidator())),
    ),
)

# use `isinstance` in python 3.8 or 3.8
assert person_validator(
    {1: "John Doe", False: 30, ("abc", 123): ["reading", "cooking"]}
) == Valid(Person("John Doe", Just(30), ["reading", "cooking"]))
