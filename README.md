# Koda Validate

Typesafe, combinable validation. Python 3.8+

Koda Validate aims to make writing validators easier. Specific areas of focus include:  
- requiring little time debugging or reading documentation 
- facilitating the building of complex validators
- reusing validator metadata (i.e. rendering API schemas)


## The Basics

```python3
from dataclasses import dataclass

from koda import Err, Ok

from koda_validate.dictionary import dict_validator, key
from koda_validate.generic import Min
from koda_validate.integer import IntValidator
from koda_validate.string import MinLength, StringValidator


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,  # <- validated values are sent to a target callable _in order_ 
    key("name", StringValidator(MinLength(1))),  # <- first key
    key("age", IntValidator(Min(0))),  # <- second key...
)

# for python >= 3.10 only. Use `if isinstance(...)` with python < 3.10
match person_validator({"name": "John Doe", "age": 30}):
    case Ok(Person(name, age)):
        print(f"{name} is {age} years old")
    case Err(errs):
        print(errs)
```

OK, cool, we can validate two fields on a dict... let's build something more complex.

```python
from dataclasses import dataclass

from koda import Err, Just, Maybe, Ok, Result, nothing

from koda_validate.dictionary import dict_validator, key, maybe_key
from koda_validate.generic import Max
from koda_validate.integer import IntValidator
from koda_validate.list import ListValidator, MinItems
from koda_validate.none import Noneable
from koda_validate.string import MaxLength, StringValidator, not_blank, strip
from koda_validate.typedefs import JSONValue


@dataclass
class Employee:
    title: str
    name: str


def no_dwight_regional_manager(employee: Employee) -> Result[Employee, JSONValue]:
    if (
        "schrute" in employee.name.lower()
        and employee.title.lower() == "assistant regional manager"
    ):
        return Err("Assistant TO THE Regional Manager!")
    else:
        return Ok(employee)


employee_validator = dict_validator(
    Employee,
    key("title", StringValidator(not_blank, MaxLength(100), preprocessors=[strip])),
    key("name", StringValidator(not_blank, preprocessors=[strip])),
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)


# the fields are valid but the object as a whole is not.
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Err("Assistant TO THE Regional Manager!")


@dataclass
class Company:
    name: str
    employees: list[Employee]
    year_founded: Maybe[int]
    stock_ticker: Maybe[str]


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
        {"title": "Regional Manager", "name": "Michael Scott"},
        {"title": " Assistant to the Regional Manager ", "name": "Dwigt Schrute"},
    ],
    "stock_ticker": "DMI",
}

assert company_validator(dunder_mifflin_data) == Ok(
    Company(
        name="Dunder Mifflin",
        employees=[
            Employee(title="Regional Manager", name="Michael Scott"),
            Employee(title="Assistant to the Regional Manager", name="Dwigt Schrute"),
        ],
        year_founded=nothing,
        stock_ticker=Just(val="DMI"),
    )
)

# we could keep nesting, arbitrarily
company_list_validator = ListValidator(company_validator)

```
It's worth stopping and mentioning a few points about the above:
- this is all typesafe in mypy without any plugins 
- we explicitly return `Err` or `Ok` objects, instead of `raise`-ing errors 
- we can validate lists, dicts, strings, etc., either on their own or nested
- it is relatively simple to write

## Validation Errors

```python
from dataclasses import dataclass

from koda import Err, Maybe

from koda_validate.processors import strip
from koda_validate.validators.dicts import dict_validator
from koda_validate.validators.validators import (
  Choices,
  Min,
  key,
  maybe_key,
)
from koda_validate.integer import IntValidator
from koda_validate.string import StringValidator, not_blank, MinLength

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
```

Note that while extra keys are invalid, there are several ways of dealing with empty keys in this
library
- maybe_key: the key does not need to be present
- Noneable: the value can be `None` or valid according to some validator 
- OneOf2: one of two different validators can be valid 
- OneOf3: one of three different validators can be valid

## Validators, Predicates, and Extension
There are two kinds of `Callable`s used for validation in Koda Validate: `Validator`s and `Predicate`s. `Validator`s 
can take an input of one type and produce a valid result of another type; or they can adjust the value (They can also
leave the same type and/or value intact). Commonly validators are used for taking data of type `Any` and validating 
that it conforms to some type or data shape. As an example, we'll write a simple `Validator` for `float`s here:

```python
from typing import Any
from koda import Result, Ok, Err
from koda_validate.typedefs import Validator, JSONValue


class SimpleFloatValidator(Validator[Any, float, JSONValue]):
    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return Ok(val) 
        else:
            return Err("expected a float")
```

What is this doing? 
- extending `Validator`, using the following types:
  - `Any`: type of input allowed
  - `float`: the type of the validated data
  - `JSONValue`: the type of the error in case of invalid data
- wrapping the submitted `val` in an `Ok` and returning it if `val` is a `float` 
- wrapping an error message in `Err` if `val` is not a float 

This is all well and good, but we'll probably want to be able to validate against values of the floats, such as  
min or max checks. For this we use `Predicate`s. This is what the `FloatValidator` in Koda Validate looks like:

```python
from typing import Any

from koda import Err, Result

from koda_validate.typedefs import JSONValue, Predicate, Validator
from koda_validate.utils import accum_errors_json


class FloatValidator(Validator[Any, float, JSONValue]):
  def __init__(self, *predicates: Predicate[float, JSONValue]) -> None:
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
from koda_validate.float import FloatValidator


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

Notice that in `Predicate`s we define `is_valid` and `err_message` methods, while in `Validator`s we define the 
entire `__call__` method. This is because `Predicate`s is coded in such a way that we limit how much it can actually 
do -- we don't want it to be able to change the value being validated during validation. This turns out to be
useful because it allows us to proceed sequentially through many `Predicate`s of the same type with the
same value. It's the reason we can be confident that we can return all `Predicate` errors for a given `Validator`.  

## Metadata
Previously we said an aim of Koda Validate is to allow reuse of validator metadata. Principally this 
is useful in generating descriptions of the validator's constraints -- one example could be generating
an OpenAPI (or other) schema. Here we'll use validator metadata to build a function which can return very simple 
plaintext descriptions of validators:

```python3
from typing import Any

from koda_validate.typedefs import Validator, Predicate
from koda_validate.string import StringValidator, MaxLength, MinLength


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
All we're doing here, of course, is writing an interpreter. For the sake of brevity it can't do much, but it's
straightforward to extend the logic. This is easy to do because, while the validators are `Callable`s at their 
core, they are also classes that can easily be inspected. (This ease of inspection is the primary reason we use
classes _at all_ in Koda Validate.) Interpreters are the recommended way to re-use validator metadata for 
non-validation purposes.


## Caveats 

### `dict_validator` max keys limit
By default `dict_validator` can have a maximum of 20 keys. You can change this by generating code
and storing it in your project:
```bash
# allow up to 30 keys
python /path/to/koda-validate/codegen/generate.py /your/target/directory --num-keys 30
```
This limitation exists because computation starts to get expensive for type checkers above a certain level, and 
it's not common to have that many keys in a dict.

### `dict_validator` types may be hard to read / slow for your editor or type-checker
`dict_validator` is a convenience function that delegates to different `Validator`s depending 
on the number of keys -- for example, `Dict2KeysValidator`, `Dict3KeysValidator`, etc. These
numbered validators are limited to a specific number of keys and can be used to mitigate
such issues.

### `dict_validator`'s keys only allow for strings
This should be resolved in a later release.
