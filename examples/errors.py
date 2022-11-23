from dataclasses import dataclass

from koda import Maybe

from koda_validate import *
from koda_validate.base import DictErrs, ExtraKeysErr, TypeErr, key_missing_err

# Wrong type
assert StringValidator()(None) == Invalid(TypeErr(str, "expected a string"))

# All failing `Predicate`s are reported (not just the first)
str_choice_validator = StringValidator(MinLength(2), Choices({"abc", "yz"}))
assert str_choice_validator("") == Invalid([MinLength(2), Choices({"abc", "yz"})])


@dataclass
class City:
    name: str
    region: Maybe[str]


city_validator = RecordValidator(
    into=City,
    keys=(
        ("name", StringValidator(not_blank)),
        ("region", KeyNotRequired(StringValidator(not_blank))),
    ),
)

# We use the key "__container__" for object-level errors
assert city_validator(None) == Invalid(TypeErr(dict, "expected a dictionary"))

# Missing keys are errors
print(city_validator({}))
assert city_validator({}) == Invalid(DictErrs({"name": key_missing_err}))

# Extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Invalid(ExtraKeysErr({"name", "region"}))


@dataclass
class Neighborhood:
    name: str
    city: City


neighborhood_validator = RecordValidator(
    into=Neighborhood,
    keys=(("name", StringValidator(not_blank)), ("city", city_validator)),
)

# Errors are nested in predictable manner
assert neighborhood_validator({"name": "Bushwick", "city": {}}) == Invalid(
    DictErrs({"city": DictErrs({"name": key_missing_err})})
)
