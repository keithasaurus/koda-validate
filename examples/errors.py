from dataclasses import dataclass

from koda import Err, Maybe

from koda_validate.dictionary import dict_validator, key, maybe_key
from koda_validate.generic import Choices, Min
from koda_validate.integer import IntValidator
from koda_validate.string import MinLength, StringValidator, not_blank, strip

# wrong type
assert StringValidator()(None) == Err(["expected a string"])

# all failing `Predicate`s are reported (not just the first)
str_choice_validator = StringValidator(MinLength(2), Choices({"abc", "yz"}))
assert str_choice_validator("") == Err(
    ["minimum allowed length is 2", "expected one of ['abc', 'yz']"]
)


@dataclass
class City:
    region: str
    population: Maybe[int]


city_validator = dict_validator(
    City,
    key("region", StringValidator(not_blank, preprocessors=[strip])),
    maybe_key("population", IntValidator(Min(0))),
)

# all errors are json serializable. we use the key "__container__" for object-level errors
assert city_validator(None) == Err({"__container__": ["expected a dictionary"]})

# required key is missing
assert city_validator({}) == Err({"region": ["key missing"]})

# extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Err(
    {"__container__": ["Received unknown keys. Only expected ['population', 'region']"]}
)
