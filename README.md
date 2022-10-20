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
allow for modification of the input either in its type or in it's value.

```python
from typing import Any

from koda import Result, Err

from koda_validate.typedefs import Validator, JSONValue, Predicate
from koda_validate.validators.validators import accum_errors_json



class FloatValidator(Validator[Any, float, JSONValue]):
    """ 
    extends `Validator` and does the following:
    - validates input of type `Any`
    - if valid, produces a `float`
    - if invalid, produces a `JSONValue`  
    """
    def __init__(self, *predicates: Predicate[float, JSONValue]) -> None:
        """
        A series of predicates allows us to check the float's _value_ in 
        as many ways as needed
        """
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, JSONValue]:
        if isinstance(val, float):
            return accum_errors_json(val, self.predicates)
        else:
            return Err(["expected a float"])

```

```python3
from koda import Ok
from koda_validate.validators import StringValidator, Err
from koda_validate.validators import not_blank, MaxLength

string_validator = StringValidator()

assert string_validator("s") == Ok("s")
assert string_validator(None) == Err(["expected a string"])

string_validator = StringValidator(not_blank, MaxLength(5))

assert string_validator("too long") == Err(["cannot be blank", "maximum allowed length is 5"])
assert string_validator("neat") == Ok("neat")
```

You might notice that we return errors from all failing value-level (as opposed to type-level) validators, 
instead of failing and exiting on the first error. This is possible because of certain type-level guarantees within
Koda Validate, but we'll get into that later.

One thing to note is that we can express validators with
multiple acceptable types. A common need is to be able to express
values that can be some concrete type or `None`. For this case we
have `Noneable`

```python
from koda_validate.validators import Noneable, IntValidator
from koda import Ok

validator = Noneable(IntValidator())

assert validator(5) == Ok(5)
assert validator(None) == Ok(None)
```

Some other utilities for expressing multiple valid forms of input is with
`OneOf2` and `OneOf3`
```python
from koda import First, Ok, Second, Err

from koda_validate.validators import IntValidator, StringValidator, OneOf2

validator = OneOf2(StringValidator(), IntValidator())

assert validator("ok") == Ok(First("ok"))
assert validator(5) == Ok(Second(5))


assert validator(None) == Err({
    'variant 1': ['expected a string'],
    'variant 2': ['expected an integer']
})

```


## What is a validator?

A simple approach to a validators could start with predicates. A predicate is simply
a function which takes some value and returns `True` or `False`:
```python3
from typing import Callable, TypeVar

A = TypeVar('A')

Predicate = Callable[[A], bool]
```
However, in the opinion of this library, this is not sufficient. We also want to be able (though not required) to:
- coerce submitted data into some other form (e.g. normalization, quantization, type conversions, etc.) 
- produce useful messages for validation failure

Given these requirements, the definition of a `Validator` would become:
```python3
from typing import Callable, TypeVar
from koda import Result

A = TypeVar('A')
Valid = TypeVar('Valid')
Invalid = TypeVar('Invalid')

Validator = Callable[[A], Result[Valid, Invalid]]
```
Some examples of validators made in this way could be:
```python3
from typing import Any
from koda import Result, Ok, Err

def is_int(val: Any) -> Result[int, str]:
    try:
        return Ok(int(val))
    except Exception:
        return Err("must be an integer")

def positive_int(val: int) -> Result[int, str]:
    if val > 0:
        return Ok(val)
    else:
        return Err("must be greater than 0")
```
It's worth noting that `positive_int` doesn't change the value, but it
still abides by the signature:
```python3
Callable[[A], Result[Valid, Invalid]]
```
In this case `A` and `Valid` happen to be the same type. Even though our
base type signature says the type of a validated input can change,
it doesn't mean it has to. In fact, in many instances, it's beneficial know
that the type and/or value of the input *do not* change.

Imagine we want to run a series of validators against an `int` value. If
we want to store these validators in a homogeneous collection, like a `list`, we'll
need the types of all the validators to be the same. In effect, this constraint also
enforces that the input and output types are the same. For example,
this works:
```python3
validators: list[Callable[[int], Result[int, str]]] = [...]
```
But this doesn't:
```python3
validators: list[Callable[[int], Result[str, str]]] = [...]
```
This second example doesn't work because if the output for a valid value is
a `str`, it cannot be valid input for the next validator in the `list`, 
since all validators in the `validators` list require an `int` argument.

Even with the types resolved, one problem we still have in this scenario cannot be 
solved by type signatures alone: even if the type is the same, we can't tell if the 
valid returned value is the same value as the input. For this reason, we have 
the notion of a "predicate validator": a wrapper function that accepts a predicate 
and an error message. A first draft might look like this:

```python3
def predicate_validator(
        predicate: Callable[[A], bool],
        error_data: E
) -> Callable[[A], Result[B, E]]:
    def inner(val: A) -> Result[B, E]:
        if predicate(a):
            return Ok(a)
        else:
            return Err(error_data)
    return inner

# USAGE
def is_less_than_5(val: int) -> bool:
    return val < 5

less_than_5_validator = predicate_validator(is_less_than_5, "must be less than 5")

assert less_than_5_validator(2) == Ok(2)
assert less_than_5_validator(10) == Err("must be less than 5")
```
That might seem long-winded, but we get an important guarantee from using
`predicate_validator`: the validated value is the same as the input. 

For the purpose of preserving typed metadata for the function, `PredicateValidator`
is actually implemented as a class in this library. But it's little more than a 
function with metadata. Implementing the previous example would look like:
```python3
class LessThan5(PredicateValidator[int, str]):
    def is_valid(self, val: int) -> bool:
        return val < 5
    
    def err_message(self, val: int) -> str:
        return "must be less than 5"

less_than_5_validator = LessThan5()

assert less_than_5_validator(2) == Ok(2)
assert less_than_5_validator(10) == Err("must be less than 5")
```
