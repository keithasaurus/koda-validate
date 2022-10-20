from dataclasses import dataclass

from koda import Err, Maybe

from koda_validate.processors import strip
from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
    Choices,
    IntValidator,
    Min,
    MinLength,
    StringValidator,
    key,
    maybe_key,
    not_blank,
)

# wrong type
assert StringValidator()(None) == Err(["expected a string"])

# all failing predicates are reported (not just the first)
str_choice_validator = StringValidator(MinLength(2), Choices({"abc", "yz"}))
assert str_choice_validator("") == Err(
    ["minimum allowed length is 2", "expected one of ['abc', 'yz']"]
)


@dataclass
class City:
    region: str
    population: Maybe[str]


city_validator = dict_validator(
    City,
    key("region", StringValidator(not_blank, preprocessors=[strip])),
    maybe_key("population", IntValidator(Min(0))),
)

# all errors are json serializable. we use the key "__container__" for object-level errors
assert city_validator(None) == Err({"__container__": ["expected a dictionary"]})

# keys are missing
assert city_validator({}) == Err(
    {"region": ["key missing"], "population": ["key missing"]}
)

# extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Err(
    {"__container__": ["Received unknown keys. Only expected ['population', 'region']"]}
)
