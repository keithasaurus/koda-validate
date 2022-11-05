from dataclasses import dataclass

from koda_validate import *


@dataclass
class Person:
    name: str
    hobbies: list[str]


person_validator = DictValidator(
    keys=(
        ("name", StringValidator()),
        ("hobbies", ListValidator(StringValidator())),
    ),
    into=Person,
)

print(person_validator({"name": "Bob", "hobbies": ["eating", "running"]}))
# > Ok(Person(name='Bob', nickname=None, hobbies=['eating', 'running']))

# Or maybe we need to validate groups of people...
people_validator = ListValidator(person_validator)

print(
    people_validator(
        [
            {"name": "Bob", "hobbies": ["eating", "running"], "nickname": "That Bob"},
            {
                "name": "Alice",
                "hobbies": ["piano", "cooking"],
                "nickname": "Alice at the Palace",
            },
        ]
    )
)

# > Ok([
#     Person(name='Bob', nickname='That Bob', hobbies=['eating', 'running']),
#     Person(name='Alice', nickname='Alice at the Palace', hobbies=['piano', 'cooking'])
#   ])

# or either?
person_or_people_validator = OneOf2(person_validator, people_validator)

person_or_people_validator(
    {"name": "Bob", "nickname": None, "hobbies": ["eating", "running"]}
)
# > Ok(First(Person(name='Bob', nickname=None, hobbies=['eating', 'running'])))

print(
    person_or_people_validator(
        (
            [
                {"name": "Bob", "nickname": None, "hobbies": ["eating", "running"]},
                {"name": "Alice", "nickname": None, "hobbies": ["piano", "cooking"]},
            ]
        )
    )
)
# > Ok(Second([
#     Person(name='Bob', nickname=None, hobbies=['eating', 'running']),
#     Person(name='Alice', nickname=None, hobbies=['piano', 'cooking'])
#   ]))
