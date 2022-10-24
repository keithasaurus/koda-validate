# Koda Validate

Typesafe, combinable validation. Python 3.8+

Koda Validate aims to make writing validators easier.

### Install
pip
```bash
pip install koda_validate
```
Poetry
```bash
poetry add koda_validate
```

## The Basics

```python3
from dataclasses import dataclass
from koda import Ok
from koda_validate import *


@dataclass
class Person:
    name: str
    age: int


person_validator = dict_validator(
    Person, 
    key("name", StringValidator()),
    key("age", IntValidator())
)

result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Ok):
    print(f"{result.val.name} is {result.val.age} years old")
else:
    print(result.val)
```

We could also nest `person_validator`, for instance, in a `ListValidator`:
```python
people_validator = ListValidator(person_validator)
```
...And nest that in a different validator (and so forth...):
```python

@dataclass
class Group:
    name: str
    people: list[Person]


group_validator = dict_validator(
    Group,
    key("name", StringValidator()),
    key("people", people_validator),
)

data = {
    "name": "Arrested Development Characters",
    "people": [
        {"name": "George Bluth", "age": 70},
        {"name": "Michael Bluth", "age": 35}
    ]
}

assert group_validator(data) == Ok(
    Group(
        name='Arrested Development Characters',
        people=[
            Person(name='George Bluth', age=70),
            Person(name='Michael Bluth', age=35)
        ]
    )
)
```

Let's look at the `dict_validator` a bit closer. Its first argument can be any `Callable` that accepts the values from 
each key below it -- in the same order they are defined (the names of the keys and the `Callable` arguments do not need 
to match). For `person_validator`, we used a `Person` `dataclass`; for `Group`, we used a `Group` dataclass; but that 
does not need to be the case. Because we can use any `Callable` with matching types, this would also be valid:
```python
from koda import Ok
from koda_validate import *


def reverse_person_args_tuple(a: str, b: int) -> tuple[int, str]:
    return b, a

person_validator_2 = dict_validator(
    reverse_person_args_tuple,
    key("name", StringValidator()),
    key("age", IntValidator()),
)

assert person_validator_2({"name": "John Doe", "age": 30}) == Ok((30, "John Doe"))

```
As you see, we have some flexibility in defining what we want to get back from a validated `dict_validator`. 

Another thing to note is that, so far, the results are all wrapped in an `Ok` class. The other possibility -- when 
validation fails -- is that an `Err` instance is returned, with whatever message or object a given validator returns. 
We do not raise exceptions to express validation failure in Koda Validate. Instead, validation is treated as part of 
normal control flow.

Let's use some more features.

```python
from dataclasses import dataclass
from koda import Err, Ok, Result
from koda_validate import *


@dataclass
class Employee:
    title: str
    name: str


def no_dwight_regional_manager(employee: Employee) -> Result[Employee, Serializable]:
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


# The fields are valid but the object as a whole is not.
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Err("Assistant TO THE Regional Manager!")

```
Things to note about `employee_validator`:
- we can add additional checks -- `Predicate`s -- to validators (e.g. `not_blank`, `MaxLength`, etc.)
- we can pre-process strings for formatting (after the type is determined, but before `Predicate` validators are run)
- we have two stages of validation on dictionaries: first the keys, then the entire object, via `validate_object`
- apparently we have a problem with someone named Dwight Schrute giving himself the wrong title


Note that everything we've seen is typesafe according to mypy -- with strict settings, and without any plugins.

### The (More) Basics

We're are spending a lot of time discussing validating collections, but Koda Validator works just as seamlessly on 
simple values.

```python
from koda import Err, Ok
from koda_validate import ExactValidator, MinLength, StringValidator

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Ok("good")
assert min_length_3_validator("bad") == Err(["minimum allowed length is 4"])

exactly_5_validator = ExactValidator(5)

assert exactly_5_validator(5) == Ok(5)
assert exactly_5_validator("hmm") == Err(["expected exactly 5 (int)"])

```
Koda Validate is intended to be extendable enough to validate any type of value.

## Validation Errors

As mentioned above, errors are returned as data as part of normal control flow. All errors from built-in validators in 
Koda Validate are JSON/YAML serializable. (However, should you build your own custom validators, there is no contract 
enfocing that constraint.) Here are a few examples of the kinds of errors you can expect to see.

```python
from dataclasses import dataclass
from koda import Err, Maybe
from koda_validate import *

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


city_validator = dict_validator(
    City,
    key("name", StringValidator(not_blank)),
    maybe_key("region", StringValidator(not_blank)),
)

# We use the key "__container__" for object-level errors
assert city_validator(None) == Err({"__container__": ["expected a dictionary"]})

# Missing keys are errors
assert city_validator({}) == Err({"name": ["key missing"]})

# Extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Err({"__container__": ["Received unknown keys. Only expected ['name', 'region']"]})


@dataclass
class Neighborhood:
    name: str
    city: City


neighborhood_validator = dict_validator(
    Neighborhood, key("name", StringValidator(not_blank)), key("city", city_validator)
)

# Errors are nested in predictable manner
assert neighborhood_validator({"name": "Bushwick", "city": {}}) == Err(
    {"city": {"name": ["key missing"]}}
)

```
If you have any concerns about being able to handle specific types of key or object requirements, please see some of 
the other validators and helpers below:
- [OneOf2 / OneOf3](#oneof2--oneof3)
- [MapValidator](#mapvalidator)
- [OptionalValidator](#optionalvalidator)
- [maybe_key](#maybe_key)
- [is_dict_validator](#is_dict_validator)
- [Lazy](#lazy)


## Validators, Predicates, and Extension
Koda Validate's intention is to cover the bulk of common use cases with its built-in tools. However, it is also meant 
to provide a straightforward way to build for custom validation use-cases. Here we'll provide a quick overview of how 
custom validation logic can be implemented.

There are two kinds of `Callable`s used for validation in Koda Validate: `Validator`s and `Predicate`s. `Validator`s 
can take an input of one type and produce a valid result of another type. (While a `Validator` has the capability to 
alter a value and/or type, whether it does is entirely dependent on the given `Validator`s requirements.) Most commonly 
`Validator`s accept type `Any` and validate that it conforms to some type or data shape. As an example, we'll 
write a simple `Validator` for `float`s here:

```python
from typing import Any
from koda import Err, Ok, Result
from koda_validate.typedefs import Serializable, Validator


class SimpleFloatValidator(Validator[Any, float, Serializable]):
    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return Ok(val)
        else:
            return Err("expected a float")


float_validator = SimpleFloatValidator()
float_val = 5.5
assert float_validator(float_val) == Ok(float_val)
assert float_validator(5) == Err("expected a float")
```

What is this doing? 
- extending `Validator`, using the following types:
  - `Any`: any type of input can be passed in
  - `float`: if the data is valid, a value of type `Ok[float]` will be returned 
  - `Serializable`: if it's invalid, a value of type `Err[Serializable]` will be returned
- the `__call__` method performs any kind of validation needed, so long as the input and output type signatures -- as determined by the `Validator` type parameters - are abided

We accept `Any` because the type of input may be unknown before submitting to the `Validator`. After our 
validation in `SimpleFloatValidator` succeeds, we know the type must be `float`.   

This is all well and good, but we'll probably want to be able to validate against values of the floats, such as min, 
max, or rough equality checks. For this we use `Predicate`s. This is what the `FloatValidator` in Koda Validate looks 
like:

```python
class FloatValidator(Validator[Any, float, Serializable]):
    def __init__(self, *predicates: Predicate[float, Serializable]) -> None:
        self.predicates = predicates

    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return accum_errors_serializable(val, self.predicates)
        else:
            return Err(["expected a float"])

```

`Predicate`s are meant to validate the _value_ of a known type -- as opposed to validating at the type-level. For 
example, this is how you might write and use a `Predicate` for approximate `float` equality:

```python
import math
from dataclasses import dataclass
from koda import Err, Ok
from koda_validate import FloatValidator, Serializable, Predicate


@dataclass
class IsClose(Predicate[float, Serializable]):
    compare_to: float
    tolerance: float

    def is_valid(self, val: float) -> bool:
        return math.isclose(self.compare_to, val, abs_tol=self.tolerance)

    def err(self, val: float) -> Serializable:
        return f"expected a value within {self.tolerance} of {self.compare_to}"


# let's use it
close_to_validator = FloatValidator(IsClose(0.05, 0.02))
a = 0.06
assert close_to_validator(a) == Ok(a)
assert close_to_validator(0.01) == Err(["expected a value within 0.02 of 0.05"])

```

Notice that in `Predicate`s we define `is_valid` and `err` methods, while in `Validator`s we define the 
entire `__call__` method. This is because the base `Predicate` class is constructed in such a way that we limit how 
much it can actually do -- we don't want it to be able to alter the value being validated. This turns out to be useful 
because it allows us to proceed sequentially through an arbitrary amount of `Predicate`s of the same type in a given 
`Validator`. Only because of this property can we be confident in our ability to return all `Predicate` errors for a 
given `Validator` -- instead of having to exit at the first failure.

## Metadata
Previously we said an aim of Koda Validate is to allow reuse of validator metadata. Principally this 
is useful in generating descriptions of the validator's constraints -- one example could be generating
an OpenAPI (or other) schema. Here we'll do something simpler and use validator metadata to build a function which can 
return plaintext descriptions of validators:

```python3
from typing import Any
from koda_validate import MaxLength, MinLength, Predicate, StringValidator, Validator


def describe_validator(validator: Validator[Any, Any, Any] | Predicate[Any, Any]) -> str:
    # use `isinstance(...)` in python <= 3.10
    match validator:
        case StringValidator(predicates):
            predicate_descriptions = [
                f"- {describe_validator(pred)}" for pred in predicates
            ]
            return "\n".join(["validates a string"] + predicate_descriptions)
        case MinLength(length):
            return f"minimum length {length}"
        case MaxLength(length):
            return f"maximum length {length}"
        # ...etc
        case _:
            raise TypeError(f"unhandled validator type. got {type(validator)}")


print(describe_validator(StringValidator()))
# validates a string
print(describe_validator(StringValidator(MinLength(5))))
# validates a string
# - minimum length 5
print(describe_validator(StringValidator(MinLength(3), MaxLength(8))))
# validates a string
# - minimum length 3
# - maximum length 8

```
All we're doing here, of course, is writing an interpreter. For the sake of brevity this one is very simple, but it's
straightforward to extend the logic. This is easy to do because, while the validators are `Callable`s at their 
core, they are also classes that can easily be inspected. (This ease of inspection is the primary reason we use
classes in Koda Validate.) Interpreters are the recommended way to re-use validator metadata for 
non-validation purposes.

## Other Noteworthy Validators and Utilities 


#### OneOf2 / OneOf3

OneOfN validators are useful when you may have multiple valid shapes of data.
```python
from koda import First, Ok, Second

from koda_validate import ListValidator, OneOf2, StringValidator

string_or_list_string_validator = OneOf2(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Ok(First("ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Ok(
    Second(["list", "of", "strings"])
)
```


#### Tuple2 / Tuple3

TupleN validators work as you might expect:
```python
from koda import Ok
from koda_validate import IntValidator, StringValidator, Tuple2Validator

string_int_validator = Tuple2Validator(StringValidator(), IntValidator())

assert string_int_validator(("ok", 100)) == Ok(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Ok(("ok", 100))

```


#### Lazy
`Lazy`'s main purpose is to allow for the use of recursion in validation. An example use case of this might be replies
in a comment thread. This can be done with mutually recursive functions. For simplicity, here's an example of parsing a 
kind of non-empty list.

```python
from typing import Optional
from koda import Ok
from koda_validate import IntValidator, Lazy, OptionalValidator, Tuple2Validator

NonEmptyList = tuple[int, Optional["NonEmptyList"]]


def recur_non_empty_list() -> Tuple2Validator[int, Optional[NonEmptyList]]:
    return non_empty_list_validator


non_empty_list_validator = Tuple2Validator(
    IntValidator(),
    OptionalValidator(Lazy(recur_non_empty_list)),
)

assert non_empty_list_validator((1, (1, (2, (3, (5, None)))))) == Ok(
    (1, (1, (2, (3, (5, None)))))
)

```


#### MapValidator

`MapValidator` allows us to validate dictionaries that are mappings of one type to another type, where we don't
need to be concerned about individual keys or values:

```python
from koda import Ok
from koda_validate import IntValidator, MapValidator, StringValidator

str_to_int_validator = MapValidator(StringValidator(), IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Ok(
    {"a": 1, "b": 25, "xyz": 900}
)

```

#### OptionalValidator

`OptionalValidator` is very simple. It validates a value is either `None` or passes another validator's rules.

```python
from koda import Ok
from koda_validate import IntValidator, OptionalValidator

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Ok(5)
assert optional_int_validator(None) == Ok(None)

```

#### maybe_key
`maybe_key` allows for a key to be missing from a dictionary

```python
from dataclasses import dataclass
from koda import Just, Maybe, Ok, nothing
from koda_validate import IntValidator, StringValidator, dict_validator, key, maybe_key


@dataclass
class Person:
    name: str
    age: Maybe[int]


person_validator = dict_validator(
    Person, key("name", StringValidator()), maybe_key("age", IntValidator())
)
assert person_validator({"name": "Bob"}) == Ok(Person("Bob", nothing))
assert person_validator({"name": "Bob", "age": 42}) == Ok(Person("Bob", Just(42)))

```

#### is_dict_validator

A very simple validator that only validates that and object is a dict. It doesn't do any validation against keys or
values.

```python
from koda import Ok, Err
from koda_validate.dictionary import is_dict_validator

assert is_dict_validator({}) == Ok({})
assert is_dict_validator(None) == Err({"__container__": ["expected a dictionary"]})
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Ok(
    {"a": 1, "b": 2, 5: "xyz"}
)

```

## Limitations

#### `dict_validator` has a max keys limit

By default `dict_validator` can have a maximum of 20 keys. You can change this by generating code
and storing it in your project:
```bash
# allow up to 30 keys
python /path/to/koda-validate/codegen/generate.py /your/target/directory --num-keys 30
```
This limitation exists because computation starts to get expensive for type checkers above a certain level, and 
it's not common to have that many keys in a dict.


#### `dict_validator` types may be hard to read / slow for your editor or type-checker**

`dict_validator` is a convenience function that delegates to different `Validator`s depending 
on the number of keys -- for example, `Dict2KeysValidator`, `Dict3KeysValidator`, etc. These
numbered validators are limited to a specific number of keys and can be used to mitigate
such issues.


#### `dict_validator`'s keys only allow for strings

This should be resolved in a later release.


#### Your Imagination
:sparkles:


### Something's Missing Or Wrong 
Open an [issue on GitHub](https://github.com/keithasaurus/koda-validate/issues) please!
