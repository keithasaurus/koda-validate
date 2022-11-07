# Koda Validate

Validate Anything. Faster!

Koda Validate is:
- type-driven (works with type hints)
- easily inspected -- build API schemas from validators
- fully asyncio-compatible


### Contents
- [Installation](#install)
- [The Basics](#the-basics)
- [Philosophy](#philosophy)
  - [Validators](#validator)
  - [Predicates](#predicates)
  - [Processors](#processors)
- [Async Validation](#async-validation)
- Extension
  - Validators
  - Predicates
  - Processors
- Tour 
  - StringValidator
  - IntValidator
  - FloatValidator
  - NoneValidator
  - DecimalValidator
  - OptionalValidator
  - ListValidator
  - DictValidator
  - DictValidatorAny
  - MapValidator
  - is_dict_validator 
  - OneOf2/OneOf3
  - Tuple2/Tuple3
- Limitations
- How does this compare to pydantic?


### Installation
pip
```bash
pip install koda-validate
```
Poetry
```bash
poetry add koda-validate
```

## The Basics

#### Scalars
```python3
from koda_validate import StringValidator

string_validator = StringValidator()

string_validator("hello world")
# > Valid('hello world')

string_validator(5)
# > Invalid(['expected a string'])

```

#### Lists
```python3
from koda_validate import *

validator = ListValidator(StringValidator())

validator(["cool"])
# > Valid(['cool'])

validator([5])
# > Invalid({'0': ['expected a string']}))
```

#### Dictionaries
```python
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
    into=Person
)

print(person_validator({"name": "Bob",
                        "hobbies": ["eating", "running"]}))
# > Valid(Person(name='Bob', hobbies=['eating', 'running']))
```

Here's what we've seen so far:
- All validators we've created are simple `Callable`s that return an `Ok` instance when validation succeeds, or an `Invalid` instance when validation fails.
- Nesting one validator within another is straightforward
- `DictValidator` requires a separate target for its validated data; more on that here.

It's worth noting that all this code is typesafe. And for similar 
equivalent validations in Pydantic, Koda Validate can be up to 15x faster.

## Philosophy
At it's core, Koda Validate is based on a few simple ideas about what validation _is_. This 
allows Koda Validate to be flexible enough to be able to validate anything. It also generally allows for 
less code, and clearer paths to opimization than other approaches.

### Validators
In Koda Validate a `Validator` is the fundamental validation building block. It's based on the idea that  
validation can be universally represented by the function signature (pseudocode) `InputType -> ValidType | InvalidType`. In
Koda Validate this looks more like `Callable[[InputType], Validated[ValidType, InvalidType]]`. A quick example:
```python
from koda_validate import IntValidator, Valid, Invalid

int_validator = IntValidator()

assert int_validator(5) == Valid(5)
assert int_validator("not an integer") == Invalid(["expected an integer"])
```
Here, we can tell the type of `int_validator` is something like `Callable[[Any], Validated[int, List[str]]` (it's not exactly 
that in reality, but it isn't far off.) In this case, the `InputType` is `Any` -- any kind of data can be submitted to validation; if the data is valid it returns `Valid[int]`; and
if it's invalid it returns `Invalid[List[str]]`. 

This is a useful model to have for validation, because it means we can **combine**
validators in different ways (i.e. nesting them), and have our model of validation be consistent throughout. In theory, we 
should be able to validate anything with this approach.

Take a look at [Extension](#extension) to see how to build custom `Validator`s.

### Predicates
In validation, predicates are simple expressions that return a `True` or `False` for a given condition. Koda Validate uses predicates to 
_enrich_ `Validator`s. Because `Validator`s might return different types and values in their valid state than in their input,
it's difficult to do something like apply a list of `Validator`s to a given value:
even _if_ the types all match up, there's no assurance that the values won't change from one validator to the next. 

The role of a `Predicate` in Koda Validate is to perform additional validation _after_ the data has been verified to be 
of a specific type. To this end, `Predicate`s in Koda Validate cannot change their input types or values. Let's go further with our `IntValidator`:
```python
from koda_validate import * 

int_validator = IntValidator(Min(5))

assert int_validator(6) == Valid(6)

assert int_validator(4) == Invalid(["minimum allowed value is 5"])
```
In this example `Min(5)` is a `Predicate`. Because we know that predicates don't change the type or value of their inputs, we can 
sequence an arbitrary number of them, and validate them all.

```python
from koda_validate import * 

int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

assert int_validator(12) == Valid(12)

assert int_validator(23) == Invalid([
  "maximum allowed value is 20",
  "must be a multiple of 4"
])
```
Here we have 3 `Predicate`s, but we could easily have dozens. Note that the errors from all invalid
predicates are returned. This is possible because we know that the value should be consistent from one predicate to the next.

`Predicate`s are easy to write -- take a look at [Extension](#extension) for more details.


### Processors
`Processor`s allow us to take a value of a given type and transform it into another value of a given type. Processors are most useful
_after_ type validation, but _before_ predicates are checked. Here's an example:
```python
from koda_validate import *

max_length_3_validator = StringValidator(
  MaxLength(3),
  preprocessors=[strip, upper_case]
)

assert max_length_3_validator(" hmm ") == Valid("HMM")
```
We see that the `preprocessors` stripped the whitespace from `" hmm "` and then transformed it to upper-case before
it was checked against the `MaxLength(3)` `Predicate`. 

Processors are very simple to write -- see [Extension](#extension) for more details.

## Extension
Koda Validate aims to provide enough tools to handle most common validation needs; for the cases it doesn't
cover, it aims to allow easy extension. Again, because Koda Validate is built on simple principles, it should be able
to validate practically any kind of data using Koda Validate's base types.


```python
from typing import Any
from koda_validate import * 


class SimpleFloatValidator(Validator[Any, float, Serializable]):
    def __call__(self, val: Any) -> Validated[float, Serializable]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid("expected a float")


float_validator = SimpleFloatValidator()

test_val = 5.5

assert float_validator(test_val) == Valid(test_val)

assert float_validator(5) == Invalid("expected a float")
```

What is this doing? 
- extending `Validator`, using the following types:
  - `Any`: any type of input can be passed in to be validated
  - `float`: if the data is valid, a value of type `Valid[float]` will be returned 
  - `Serializable`: if it's invalid, a value of type `Invalid[Serializable]` will be returned
- the `__call__` method performs any kind of validation needed, so long as the input and output type signatures -- as determined by the `Validator` type parameters - are abided

We accept `Any` because the type of input may be unknown before submitting to the `Validator`. After our 
validation in `SimpleFloatValidator` succeeds, we know the type must be `float`. Note that we could have coerced the value
to a `float` instead of checking its type -- that is 100% OK to do. For simplicity's sake, this validator does not coerce.

This is all well and good, but we'll probably want to be able to validate against values of the floats, such as min, 
max, or rough equality checks. For this we use `Predicate`s. For exmaple, if we wanted to allow a single predicate in 
our `SimpleFloatValidator` we could do it like this:

```python
from dataclasses import dataclass
from typing import Any, Optional
from koda_validate import *

@dataclass
class SimpleFloatValidator2(Validator[Any, float, Serializable]):
    predicate: Optional[Predicate[float, Serializable]] = None

    def __call__(self, val: Any) -> Validated[float, Serializable]:
        if isinstance(val, float):
            if self.predicate:
                return self.predicate(val)
            else:
                return Valid(val)
        else:
            return Invalid(["expected a float"])

```
Here we allow for a single predicate to be specified. If it is specified, we'll check it _after_ we've verified the type of the value.

`Predicate`s are meant to validate the _value_ of a known type -- as opposed to validating at the type-level (that's what the `Validator` does). 
For example, this is how you might write and use a `Predicate` to validate a range of values:

```python
# (continuing from previous example)

@dataclass
class Range(Predicate[float, Serializable]):
    minimum: float
    maximum: float

    def is_valid(self, val: float) -> bool:
        return self.minimum <= val <= self.maximum

    def err(self, val: float) -> Serializable:
        return f"expected a value in the range of {self.minimum} and {self.maximum}"


range_validator = SimpleFloatValidator2(Range(0.5, 1.0))
test_val = 0.7

assert range_validator(test_val) == Valid(test_val)

assert range_validator(0.01) == Invalid(["expected a value in the range of 0.5 and 1.0"])

```

Notice that in `Predicate`s we define `is_valid` and `err` methods, while in `Validator`s we define the 
entire `__call__` method. This is because the base `Predicate` class is constructed in such a way that we limit how 
much it can actually do -- we don't want it to be able to alter the value being validated.

Finally, let's add a `Processor`. For whatever reason, we want to preprocess our `float`s by converting them to their
absolute value.

```python
# (continuing from previous example)

@dataclass
class SimpleFloatValidator3(Validator[Any, float, Serializable]):
    predicate: Optional[Predicate[float, Serializable]] = None
    preprocessor: Optional[Processor[float]] = None

    def __call__(self, val: Any) -> Validated[float, Serializable]:
        if isinstance(val, float):
            if self.preprocessor:
                val = self.preprocessor(val)

            if self.predicate:
                return self.predicate(val)
            else:
                return Valid(val)
        else:
            return Invalid(["expected a float"])


class AbsValue(Processor[float]):
    def __call__(self, val: float) -> float:
        return abs(val)


range_validator_2 = SimpleFloatValidator3(
    predicate=Range(0.5, 1.0),
    preprocessor=AbsValue()
)

test_val = -0.7

assert range_validator_2(test_val) == Valid(abs(test_val))

assert range_validator_2(-0.01) == Invalid('expected a value in the range of 0.5 and 1.0')
```
Note that we pre-process _before_ the predicates are run. This is the general approach Koda Validate takes on built-in 
validators. More specifically, the built in validators consider there to be a pipeline of actions taken within a validator:
`type-check/coerce -> preprocess -> validate predicates`, where it can fail at either the first or last stage.

Note that what we've written are a number of classes that conform to some type constraints. It's worth remembering that
there's nothing enforcing the particular arrangement of logic we have in our `SimpleFloatValidator`. If you want to have a 
post-processing step, you can. If you want to validate an iso8601 string is a datetime, and then convert that to an unix 
epoch timestamp, and provide pre-processing, post-processing and predicates for all those steps, you can. It's important 
to remember that our `Validator`, `Predicate`, and `Processor` objects are little more than functions with accessible metadata. 
You can do whatever you want with them.

## Async Validation
Because Koda Validate is based on simple principles, it's relatively straightforward to make it compatible with `asyncio`.
All the built-in `Validator`s in Koda are asyncio-compatible -- all you need to do is call a `Validator` in this form 
`await validator.validate_async("abc")`, instead of `validator("abc")`. 
```python
import asyncio
from koda_validate import *


short_string_validator = StringValidator(MaxLength(10))

assert short_string_validator("sync") == Valid("sync")

# we're not in an async context, so we can't use `await` here
assert asyncio.run(short_string_validator.validate_async("async")) == Valid("async")
```

This example isn't particularly helpful because we aren't doing any asynchronous IO. It would be much more 
useful if we were doing something like querying a database:
```python
import asyncio
from koda_validate import *


class IsActiveUsername(PredicateAsync[str, Serializable]):
    async def is_valid_async(self, val: str) -> bool:
        # add some latency to pretend we're calling the db
        await asyncio.sleep(.01)

        return val in {"michael", "gob", "lindsay", "buster"}

    async def err_async(self, val: str) -> Serializable:
        return "invalid username"


username_validator = StringValidator(MinLength(1),
                                     MaxLength(100),
                                     predicates_async=[IsActiveUsername()])

assert asyncio.run(username_validator.validate_async("michael")) == Valid("michael")
assert asyncio.run(username_validator.validate_async("tobias")) == Invalid(["invalid username"])
```
In this example we are calling the database to verify a username. A few things worth pointing out:
`PredicateAsync`s are specified in `predicates_async` -- separately from `Predicates`. We do this to be explicit, we 
don't want to be confused about whether a validator requires asyncio. (If you try to run this validator in synchronous mode, it 
will raise an `AssertionError` -- instead make sure you call it like `await username_validator.validate_async("buster")`.)


```python
# Or maybe we need to validate groups of people...
people_validator = ListValidator(person_validator)

print(people_validator([{"name": "Bob", "hobbies": ["eating", "running"], "nickname": "That Bob"},
                        {"name": "Alice", "hobbies": ["piano", "cooking"], "nickname": "Alice at the Palace"}]))

# > Valid([
#     Person(name='Bob', nickname='That Bob', hobbies=['eating', 'running']),
#     Person(name='Alice', nickname='Alice at the Palace', hobbies=['piano', 'cooking'])
#   ])

# or either?
person_or_people_validator = OneOf2(person_validator, people_validator)

person_or_people_validator({"name": "Bob", "nickname": None, "hobbies": ["eating", "running"]})
# > Valid(First(Person(name='Bob', nickname=None, hobbies=['eating', 'running'])))

print(person_or_people_validator(([
    {"name": "Bob", "nickname": None, "hobbies": ["eating", "running"]},
    {"name": "Alice", "nickname": None, "hobbies": ["piano", "cooking"]}])))
# > Valid(Second([
#     Person(name='Bob', nickname=None, hobbies=['eating', 'running']), 
#     Person(name='Alice', nickname=None, hobbies=['piano', 'cooking'])
#   ]))

```

A few things to note:
- All validators we've made are simple callables that either return and `Ok` or `Invalid` instance.
- We can easily combine and re-use validators, by nesting one in another, for instance.


Let's look at the `dict_validator` a bit closer. Its `into` argument can be any `Callable` that accepts the values from 
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

assert person_validator_2({"name": "John Doe", "age": 30}) == Valid((30, "John Doe"))

```
As you see, we have some flexibility in defining what we want to get back from a validated `dict_validator`. 

Another thing to note is that, so far, the results are all wrapped in an `Ok` class. The other possibility -- when 
validation fails -- is that an `Invalid` instance is returned, with whatever message or object a given validator returns. 
We do not raise exceptions to express validation failure in Koda Validate. Instead, validation is treated as part of 
normal control flow.

Let's use some more features.

```python
from dataclasses import dataclass
from koda import Invalid, Ok, Result
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
        return Invalid("Assistant TO THE Regional Manager!")
    else:
        return Valid(employee)


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
) == Invalid("Assistant TO THE Regional Manager!")

```
Things to note about `employee_validator`:
- we can add additional checks -- `Predicate`s -- to validators (e.g. `not_blank`, `MaxLength`, etc.)
- we can pre-process strings for formatting (after the type is determined, but before `Predicate` validators are run)
- we have two stages of validation on dictionaries: first the keys, then the entire object, via `validate_object`
- apparently we have a problem with someone named Dwight Schrute giving himself the wrong title


Note that everything we've seen is typesafe according to mypy -- with strict settings, and without any plugins.

### The (More) Basics

We're are spending a lot of time discussing validating collections, but Koda Validate works just as well on simple 
values.

```python
from koda import Invalid, Ok
from koda_validate import ExactValidator, MinLength, StringValidator

min_length_3_validator = StringValidator(MinLength(4))
assert min_length_3_validator("good") == Valid("good")
assert min_length_3_validator("bad") == Invalid(["minimum allowed length is 4"])

exactly_5_validator = ExactValidator(5)

assert exactly_5_validator(5) == Valid(5)
assert exactly_5_validator("hmm") == Invalid(["expected exactly 5 (int)"])

```
Koda Validate is intended to be extendable enough to validate any type of data.

## Validation Invalidors

As mentioned above, errors are returned as data as part of normal control flow. The contents of all returned `Invalid`s 
from built-in validators in Koda Validate are JSON/YAML serializable. (However, should you build your own custom 
validators, there is no contract enforcing that constraint.) Here are a few examples of the kinds of errors you can 
expect to see out of the box.

```python
from dataclasses import dataclass
from koda import Invalid, Maybe
from koda_validate import *

# Wrong type
assert StringValidator()(None) == Invalid(["expected a string"])

# All failing `Predicate`s are reported (not just the first)
str_choice_validator = StringValidator(MinLength(2), Choices({"abc", "yz"}))
assert str_choice_validator("") == Invalid(
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
assert city_validator(None) == Invalid({"__container__": ["expected a dictionary"]})

# Missing keys are errors
assert city_validator({}) == Invalid({"name": ["key missing"]})

# Extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Invalid({"__container__": ["Received unknown keys. Only expected ['name', 'region']"]})


@dataclass
class Neighborhood:
    name: str
    city: City


neighborhood_validator = dict_validator(
    Neighborhood, key("name", StringValidator(not_blank)), key("city", city_validator)
)

# Invalidors are nested in predictable manner
assert neighborhood_validator({"name": "Bushwick", "city": {}}) == Invalid(
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
from koda import Invalid, Ok, Result
from koda_validate.typedefs import Serializable, Validator


class SimpleFloatValidator(Validator[Any, float, Serializable]):
    def __call__(self, val: Any) -> Result[float, Serializable]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid("expected a float")


float_validator = SimpleFloatValidator()
float_val = 5.5
assert float_validator(float_val) == Valid(float_val)
assert float_validator(5) == Invalid("expected a float")
```

What is this doing? 
- extending `Validator`, using the following types:
  - `Any`: any type of input can be passed in
  - `float`: if the data is valid, a value of type `Ok[float]` will be returned 
  - `Serializable`: if it's invalid, a value of type `Invalid[Serializable]` will be returned
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
            return Invalid(["expected a float"])

```

`Predicate`s are meant to validate the _value_ of a known type -- as opposed to validating at the type-level. For 
example, this is how you might write and use a `Predicate` for approximate `float` equality:

```python
import math
from dataclasses import dataclass
from koda import Invalid, Ok
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
assert close_to_validator(a) == Valid(a)
assert close_to_validator(0.01) == Invalid(["expected a value within 0.02 of 0.05"])

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
            raise TypeInvalidor(f"unhandled validator type. got {type(validator)}")


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

assert string_or_list_string_validator("ok") == Valid(First("ok"))
assert string_or_list_string_validator(["list", "of", "strings"]) == Valid(
    Second(["list", "of", "strings"])
)
```


#### Tuple2Validator / Tuple3Validator

These `Validator`s work on `tuple`s as you might expect:
```python
from koda import Ok
from koda_validate import IntValidator, StringValidator, Tuple2Validator

string_int_validator = Tuple2Validator(StringValidator(), IntValidator())

assert string_int_validator(("ok", 100)) == Valid(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Valid(("ok", 100))

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

assert non_empty_list_validator((1, (1, (2, (3, (5, None)))))) == Valid(
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

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)

```

#### OptionalValidator

`OptionalValidator` is very simple. It validates a value is either `None` or passes another validator's rules.

```python
from koda import Ok
from koda_validate import IntValidator, OptionalValidator

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Valid(5)
assert optional_int_validator(None) == Valid(None)

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
assert person_validator({"name": "Bob"}) == Valid(Person("Bob", nothing))
assert person_validator({"name": "Bob", "age": 42}) == Valid(Person("Bob", Just(42)))

```

#### is_dict_validator

A very simple validator that only validates that and object is a dict. It doesn't do any validation against keys or
values.

```python
from koda import Ok, Invalid
from koda_validate.dictionary import is_dict_validator

assert is_dict_validator({}) == Valid({})
assert is_dict_validator(None) == Invalid({"__container__": ["expected a dictionary"]})
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Valid(
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


#### `dict_validator` types may be hard to read / slow for your editor or type-checker

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
