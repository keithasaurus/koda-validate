# Koda Validate

Typesafe, combinable validation. Python 3.8+

Koda Validate aims to make writing validators easier. Specific areas of focus include:  
- requiring little time debugging or reading documentation 
- facilitating the building of complex validators
- reusing validator metadata (i.e. rendering API schemas)


## The Basics

```python3
from dataclasses import dataclass

from koda import Ok

from koda_validate.dictionary import dict_validator, key
from koda_validate.generic import Min
from koda_validate.integer import IntValidator
from koda_validate.string import MinLength, StringValidator


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person,  # <- destination of data if valid
    key("name", StringValidator(MinLength(1))),  # <- first key
    key("age", IntValidator(Min(0))),  # <- second key...
)

# note that `match` statements can be used in python >= 3.10
result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Ok):
    print(f"{result.val.name} is {result.val.age} years old")
else:
    print(result.val)

```

OK, cool, we can validate two fields on a dictionary... let's build something more complex.


```python
from dataclasses import dataclass

from koda import Err, Ok, Result

from koda_validate.dictionary import dict_validator, key
from koda_validate.list import ListValidator, MinItems
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
    # After we've validated individual fields, we may want to validate them together 
    validate_object=no_dwight_regional_manager,
)

# the fields are valid individually, but the object as a whole is not
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Err("Assistant TO THE Regional Manager!")

```
A few things to note:
- we explicitly return `Err` or `Ok` objects, instead of `raise`-ing errors 
- we can pre-process strings for formatting
- we have two stages of validation on dictionaries: first the keys, then the entire object

OK, now we'll create a validator for company data to see how easy it is to combine validators: 

```python
@dataclass
class Company:
    name: str
    employees: list[Employee]


company_validator = dict_validator(
    Company,
    key("company_name", StringValidator(not_blank, preprocessors=[strip])),
    key(
        "employees",
        ListValidator(
            employee_validator, # reusing the same validator from above
            MinItems(1),  # a company has to have at least one employee 
        ),
    ), 
)

dunder_mifflin_data = {
    "company_name": "Dunder Mifflin",
    "employees": [
        {"title": "Regional Manager", "name": "Michael Scott"},
        {"title": " Assistant to the Regional Manager ", "name": "Dwigt Schrute"},
    ],
}

assert company_validator(dunder_mifflin_data) == Ok(
    Company(
        name="Dunder Mifflin",
        employees=[
            Employee(title="Regional Manager", name="Michael Scott"),
            Employee(title="Assistant to the Regional Manager", name="Dwigt Schrute"),
        ],
    )
)

# we could keep nesting, arbitrarily
company_list_validator = ListValidator(company_validator)

```
It's worth stopping and mentioning a few points about the above:
- this is all typesafe in mypy (without any plugins)
- we can validate lists, dicts, strings, etc., either on their own or nested
- it is relatively simple to write

## Validation Errors

```python
from dataclasses import dataclass

from koda import Err, Maybe

from koda_validate.dictionary import dict_validator, key, maybe_key
from koda_validate.generic import Choices
from koda_validate.string import MinLength, StringValidator, not_blank

# wrong type
assert StringValidator()(None) == Err(["expected a string"])

# all failing `Predicate`s are reported (not just the first)
str_choice_validator = StringValidator(
    MinLength(2),
    Choices({"abc", "yz"})
)
assert str_choice_validator("") == Err(
    ["minimum allowed length is 2", "expected one of ['abc', 'yz']"]
)


@dataclass
class City:
    name: str
    region: Maybe[str]


city_validator = dict_validator(
    City,
    key("name", StringValidator(not_blank)),
    maybe_key("region", StringValidator(not_blank)),
)

# all errors are json serializable. we use the key "__container__" for object-level errors
assert city_validator(None) == Err({"__container__": ["expected a dictionary"]})

# required key is missing
assert city_validator({}) == Err({"name": ["key missing"]})

# extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Err(
    {"__container__": ["Received unknown keys. Only expected ['name', 'region']"]}
)


@dataclass
class Neighborhood:
    name: str
    city: City


neighborhood_validator = dict_validator(
    Neighborhood,
    key("name", StringValidator(not_blank)),
    key("city", city_validator)
)

# errors are nested
assert neighborhood_validator(
    {"name": "Bushwick", "city": {}}
) == Err({
    'city':
        {
            'name': ['key missing']
        }
})

```

## Validators, Predicates, and Extension
There are two kinds of `Callable`s used for validation in Koda Validate: `Validator`s and `Predicate`s. `Validator`s 
can take an input of one type and produce a valid result of another type (whether the value and/or type is altered or 
not is entirely dependent on the given `Validator`s requirements). `Validator`s commonly accept type `Any` and validate 
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
  - `Any`: any type of input can be passed in allowed
  - `float`: if it's valid a float will be returned 
  - `JSONValue`: if it's invalid JSONValue will be returned 
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

## Other Noteworthy Parts 

**OneOf2 / OneOf3**

OneOfN validators are useful when you may have multiple valid shapes of data.
```python
from koda import Ok, First, Second

from koda_validate.list import ListValidator
from koda_validate.one_of import OneOf2
from koda_validate.string import StringValidator

string_or_list_string_validator = OneOf2(
    StringValidator(),
    ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Ok(First("ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Ok(Second(["list", "of", "strings"]))
```

**Tuple2 / Tuple3**

TupleN validators work as you might expect:
```python
from koda import Ok

from koda_validate.integer import IntValidator
from koda_validate.string import StringValidator
from koda_validate.tuple import Tuple2Validator

string_int_validator = Tuple2Validator(
    StringValidator(),
    IntValidator()
)

assert string_int_validator(("ok", 100)) == Ok(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Ok(("ok", 100))
```

**Lazy**
`Lazy`'s main purpose is to allow for the use of recursion in validation. An example use case of this might be replies
in a comment thread. This can be done with mutually recursive functions, as seen below.

```python
from koda import Maybe, Ok, Just, nothing

from koda_validate.generic import Lazy
from koda_validate.integer import IntValidator
from koda_validate.none import OptionalValidator
from koda_validate.tuple import Tuple2Validator

NonEmptyList = tuple[int, Maybe["NonEmptyList"]]


def recur_non_empty_list() -> Tuple2Validator[int, Maybe[NonEmptyList]]:
  return non_empty_list_validator


non_empty_list_validator = Tuple2Validator(
  IntValidator(),
  OptionalValidator(Lazy(recur_non_empty_list)),
)

assert non_empty_list_validator((1, (1, (2, (3, (5, None)))))) == Ok(
  (1, Just((1, Just((2, Just((3, Just((5, nothing)))))))))
)

```

**MapValidator**

`MapValidator` allows us to validate dictionaries that are mappings of one type to another type, where we don't
need to be concerned about individual keys or values:

```python
from koda import Ok

from koda_validate.dictionary import MapValidator
from koda_validate.integer import IntValidator
from koda_validate.string import StringValidator

str_to_int_validator = MapValidator(StringValidator(), IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Ok({'a': 1, 'b': 25, 'xyz': 900})
```

**OptionalValidator**

`OptionalValidator` is very simple. It validates a value is either `None` or passes another validator's rules.

```python
from koda import Ok

from koda_validate.integer import IntValidator
from koda_validate.none import OptionalValidator

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Ok(5)
assert optional_int_validator(None) == Ok(None)

```


## Limitations

### `dict_validator` has a max keys limit
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
