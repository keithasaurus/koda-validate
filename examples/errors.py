from dataclasses import dataclass

from koda import Err, Maybe

from koda_validate import *
from koda_validate.dictionary import KeyNotRequired

# Wrong type
assert StringValidator()(None) == Err(["expected a string"])

# All failing `Predicate`s are reported (not just the first)
str_choice_validator = StringValidator(MinLength(2), Choices({"abc", "yz"}))
assert str_choice_validator("") == Err(
    ["minimum allowed length is 2", "expected one of ['abc', 'yz']"]
)


@dataclass
class City:
    name: str
    region: Maybe[str]


city_validator = DictValidator(
    into=City,
    keys=(
        ("name", StringValidator(not_blank)),
        ("region", KeyNotRequired(StringValidator(not_blank))),
    ),
)

# We use the key "__container__" for object-level errors
assert city_validator(None) == Err({"__container__": ["expected a dictionary"]})

# Missing keys are errors
print(city_validator({}))
assert city_validator({}) == Err({"name": ["key missing"]})

# Extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Err({"__container__": ["Received unknown keys. Only expected 'name', 'region'."]})


@dataclass
class Neighborhood:
    name: str
    city: City


neighborhood_validator = DictValidator(
    into=Neighborhood,
    keys=(("name", StringValidator(not_blank)), ("city", city_validator)),
)

# Errors are nested in predictable manner
assert neighborhood_validator({"name": "Bushwick", "city": {}}) == Err(
    {"city": {"name": ["key missing"]}}
)
