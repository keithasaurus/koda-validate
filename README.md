# Koda Validate

## The Basics

```python3
from dataclasses import dataclass

from koda import Ok, Err

from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
    StringValidator,
    MinLength,
    key,
    IntValidator,
    Min,
)


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,  # <- if successful, we'll send the validated arguments here
    key("name", StringValidator(MinLength(1))),  # <- keys we're validating for
    key("age", IntValidator(Min(0))),
)

person_data = {"name": "John Doe", "age": 30}

match person_validator(person_data):
    case Ok(Person(name, age)):
        print(f"{name} is {age} years old")
    case Err(errs):
        print(errs)

```

OK, cool, we can validate two fields on a dict... Let's build something more complex.

## Validators

```python
from dataclasses import dataclass

from koda import Ok, Maybe, nothing, Just, Result, Err

from koda_validate.processors import strip
from koda_validate.typedefs import JSONValue
from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
    IntValidator,
    Min,
    MinLength,
    StringValidator,
    key,
    not_blank,
    ListValidator,
    MinItems,
    MaxLength,
    Max,
    maybe_key,
    Noneable,
)


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,
    key("name", StringValidator(MinLength(1))),
    key("age", IntValidator(Min(0))),
)


@dataclass
class Employee:
    title: str
    person: Person


@dataclass
class Company:
    name: str
    employees: list[Employee]
    year_founded: Maybe[int]
    stock_ticker: Maybe[str]


def no_dwight_regional_manager(employee: Employee) -> Result[Employee, JSONValue]:
    if (
        "schrute" in employee.person.name.lower()
        and employee.title.lower() == "assistant regional manager"
    ):
        return Err("Assistant TO THE Regional Manager!")
    else:
        return Ok(employee)


employee_validator = dict_validator(
    Employee,
    key("title", StringValidator(not_blank, MaxLength(100), preprocessors=[strip])),
    # we can nest validators
    key("person", person_validator),
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)

assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "person": {"name": "Dwight Schrute", "age": 39},
    }
) == Err("Assistant TO THE Regional Manager!")

company_validator = dict_validator(
    Company,
    key("company_name", StringValidator(not_blank, preprocessors=[strip])),
    key(
        "employees",
        ListValidator(
            employee_validator,
            MinItems(1),  # a company has to have at least one person, right??
        ),
    ),
    # maybe_key means the key can be missing
    maybe_key("year_founded", IntValidator(Max(2022))),
    key(
        "stock_ticker",
        Noneable(StringValidator(not_blank, MaxLength(4), preprocessors=[strip])),
    ),
)

dunder_mifflin_data = {
    "company_name": "Dunder Mifflin",
    "employees": [
        {"title": "Regional Manager", "person": {"name": "Michael Scott", "age": 45}},
        {
            "title": " Assistant to the Regional Manager ",
            "person": {"name": "Dwigt Schrute", "age": 39},
        },
    ],
    "stock_ticker": "DMI",
}

assert company_validator(dunder_mifflin_data) == Ok(
    Company(
        name="Dunder Mifflin",
        employees=[
            Employee(
                title="Regional Manager", person=Person(name="Michael Scott", age=45)
            ),
            Employee(
                title="Assistant to the Regional Manager",
                person=Person(name="Dwigt Schrute", age=39),
            ),
        ],
        year_founded=nothing,
        stock_ticker=Just(val="DMI"),
    )
)

# we could keep nesting, arbitrarily
company_list_validator = ListValidator(company_validator)

```
It's worth stopping and mentioning a few points about the above:
- this is all typesafe (according to mypy)
- we can validate lists, dicts, strings, etc., either on their own or nested
- while the code is not the shortest ever, it is relative simple to write

## Validation Errors

```python
from dataclasses import dataclass

from koda import Err, Maybe

from koda_validate.processors import strip
from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
    StringValidator,
    Choices,
    MinLength,
    not_blank,
    key,
    IntValidator,
    Min,
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
    key("population", IntValidator(Min(0))),
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
```

Note that while extra keys are invalid, there are several ways of dealing with empty keys in this
library
- maybe_key
- Noneable
- OneOf2
- OneOf3

Since we are beginning to see that Koda Validate is explicit about validation, it's worth mentioning the project's aims:
- to write complex validators faster
- to spend little time debugging
- to allow reuse of validator metadata (i.e. rendering API schemas)
- to allow type-safe extension of validation logic

## Extension 
There are two kinds of callables used for validation in Koda Validate: `Validator`s and `Predicate`s. `Validator`s 
allow for modification of the input either in its type or in it's value. If you wanted to build your own `Validator`
for `float`s, you could write it like this:

```python
from typing import Any
from koda import Result, Ok, Err
from koda_validate.typedefs import Validator, JSONValue


class SimpleFloatValidator(Validator[Any, float, JSONValue]):
    """ 
    extends `Validator`:
    - `Any`: type of input allowed  
    - `float`: the type of the validated data
    - `JSONValue`: the type of the error in case of invalid data 
    """ 
    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return Ok(val) 
        else:
            return Err("expected a float")
```

This is all well and good, but we'll probably want to be able to check against values of the floats, such as setting 
min or max thresholds. For this we use `Predicate`s. This is what the `FloatValidator` in Koda Validate looks like: 


```python
from typing import Any

from koda import Err, Result

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.validators.validators import accum_errors_json


class FloatValidator(Validator[Any, float, JSONValue]):
    def __init__(self, *predicates: Predicate[float, JSONValue]) -> None:
        """
        Predicates allow us to run multiple checks on a given value
        """
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return accum_errors_json(val, self.predicates)
        else:
            return Err(["expected a float"])
```

`Predicate`s allow us to validate the _value_ of a known type. This is how you might write and use a `Predicate` 
for approximate `float` equality:

```python
import math
from dataclasses import dataclass

from koda import Ok, Err

from koda_validate.typedefs import Predicate, JSONValue
from koda_validate.validators.validators import FloatValidator


@dataclass
class IsClose(Predicate[float, JSONValue]):
    compare_to: float
    tolerance: float

    def is_valid(self, val: float) -> bool:
        return math.isclose(
            self.compare_to,
            val,
            abs_tol=self.tolerance
        )

    def err_message(self, val: float) -> JSONValue:
        return f"expected a value within {self.tolerance} of {self.compare_to}"


# let's use it
close_to_validator = FloatValidator(IsClose(.05, .02))
a = .06
assert close_to_validator(a) == Ok(a)
assert close_to_validator(.01) == Err(["expected a value within 0.02 of 0.05"])
```

In Koda Validate `Predicate`s are essentially subsets of all the possible `Validator`s, in that they still
perform validation, but the type of the input and the valid data must be the same. This turns out to be
a very useful property because it allows us to proceed sequentially through many `Predicate`s of the same 
type with the same value. Taking it one step further, Koda Validate's `Predicate` class's `__call__` method
ensures the value being validated CANNOT change during validation (mutable types not withstanding).

## Metadata
Above we said an aim of Koda Validate is "to allow reuse of validator metadata". Principally this 
is useful in generating descriptions of the validator's constraints -- one example could be generating
an OpenAPI schema. We'll use validator metadata to build a plaintext description of a validator:

```python3
from typing import Any

from koda_validate.typedefs import Validator, Predicate
from koda_validate.validators.validators import StringValidator, MinLength, MaxLength


def describe_validator(validator: Validator[Any, Any, Any] | Predicate[Any, Any]) -> str:
    match validator:
        case StringValidator(predicates):
            predicate_descriptions = [
                f"- {describe_validator(pred)}"
                for pred in predicates
            ]
            return "\n".join(["validates a string"] + predicate_descriptions)
        case MinLength(length):
            return f"minimum length {length}"
        case MaxLength(length):
            return f"maximum length {length}"
        # ...etc
        case _:
            raise TypeError(f"unhandled validator type. got {type(validator)}")


assert describe_validator(StringValidator()) == "validates a string"
assert describe_validator(StringValidator(MinLength(5))) == "validates a string\n- minimum length 5"
assert describe_validator(
    StringValidator(MinLength(3), MaxLength(8))) == "validates a string\n- minimum length 3\n- maximum length 8"

```
All we're doing here, of course, is writing an interpreter. This is easy to do because, while the validators
are `Callable`s at their core, they are also classes that can easily be inspected. (This ease of inspection is
the primary reason we use classes _at all_ in Koda Validate.) Interpreters are the recommended way to re-use
validator metadata for non-validation purposes.


## Caveats 

### dict key number limit
Currently you can have a max of 20 keys on a `dict_validator` by default. You can change this by generating code
and storing it in your project:
```bash
# allow up to 30 keys
python /path/to/koda-validate/codegen/generate.py /your/target/directory --num-keys 30
```
The reason for this is that the computation starts to get expensive for type checkers, and 
it's not common to have that many keys in a dict.

### dict key only allow for strings
This should be resolved in a later release.
