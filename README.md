# Koda Validate

Validate Anything. Faster!

Koda Validate is:
- flexible
- explicit
- fully asyncio-compatible
- type-driven (works with type hints without plugins)
- easily inspected -- build API schemas from validators


### Contents
- [Installation](#installation)
- [The Basics](#the-basics)
- [Philosophy](#philosophy)
  - [Validators](#validators)
  - [Predicates](#predicates)
  - [Processors](#processors)
- [Extension](#extension) 
- [Validation Errors](#validation-errors)
- [Async Validation](#async-validation)
- [Using Metadata](#using-metadata)
- [Tour](#tour)
- [Comparison to Pydantic](#comparison-to-pydantic)


## Installation
Python 3.8+

pip
```bash
pip install koda-validate
```
Poetry
```bash
poetry add koda-validate
```

## The Basics

### Scalars
```python3
from koda_validate import * 

string_validator = StringValidator()

string_validator("hello world")
# > Valid('hello world')

string_validator(5)
# > Invalid(['expected a string'])

```
Note that you can pattern match on validated data on python >= 3.10
```python3
# continued from above

match string_validator("new string"):
    case Valid(valid_val):
        print(f"{valid_val} is valid!")
    case Invalid(err):
        print(f"got error: {err}")

# prints: "new string is valid"
```
You can also use `.is_valid` on python >= 3.8+:

```python3
# continued from above

if (result := string_validator("another string")).__call__:
  print(f"{result.val} is valid!")
else:
  print(f"got error: {result.val}")
# prints: "another string is valid"
```
Mypy understands `.is_valid` and narrows the `Validated` type to `Valid` or `Invalid` appropriately.

### Lists
```python3
from koda_validate import *

validator = ListValidator(StringValidator())

validator(["cool"])
# > Valid(['cool'])

validator([5])
# > Invalid({'0': ['expected a string']}))

```

### Record-like Dictionaries

```python3
from dataclasses import dataclass

from koda_validate import *


@dataclass
class Person:
  name: str
  hobbies: list[str]


person_validator = RecordValidator(
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

### Map-like Dictionaries
```python3
from koda_validate import *

str_to_int_validator = MapValidator(key=StringValidator(),
                                    value=IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)

```

### Schema-ed Dictionaries  
```python3
from koda_validate import *

person_validator = DictValidatorAny({
    "name": StringValidator(),
    "age": IntValidator(),
})

result = person_validator({"name": "John Doe", "age": 30})
if isinstance(result, Valid):
    print(f"{result.val['name']} is {result.val['age']} years old")
else:
    print(result.val)

# prints: "John Doe is 30 years old"
```
Note that `DictValidatorAny` is not typesafe.

Some of what we've seen so far:
- All validators we've created are simple `Callable`s that return an `Valid` instance when validation succeeds, or an `Invalid` instance when validation fails.
- Nesting one validator within another is straightforward
- We have multiple means of validating dictionaries
- [RecordValidator](#recordvalidator) requires a separate target for its validated data; more on that [here](#recordvalidator).

It's worth noting that all this code is typesafe (aside from [DictValidatorAny](#dictvalidatorany), which is explicitly not typesafe). No plugins are required for mypy. 

## Philosophy
At it's core, Koda Validate is based on a few simple ideas about what validation _is_. This 
allows Koda Validate to be extended to validate essentially any kind of data. It also generally allows for 
less code, and clearer paths to optimization than other approaches.

### Validators
In Koda Validate, `Validator` is the fundamental validation building block. It's based on the idea that  
validation can be universally represented by the function signature (pseudocode): 
```
InputType -> ValidType | InvalidType
```
In Koda Validate this looks more like: 
```python3
Callable[[InputType], Validated[ValidType, InvalidType]]
``` 
A quick example:

```python3
from koda_validate import IntValidator, Valid, Invalid

int_validator = IntValidator()

assert int_validator(5) == Valid(5)
assert int_validator("not an integer") == Invalid(,
```
Here, we can tell the type of `int_validator` is something like `Callable[[Any], Validated[int, List[str]]` (it's not exactly 
that in reality, but it isn't far off.) In this case, the `InputType` is `Any` -- any kind of data can be submitted to validation; if the data is valid it returns `Valid[int]`; and
if it's invalid it returns `Invalid[List[str]]`. 

This is a useful model to have for validation, because it means we can **combine**
validators in different ways (i.e. nesting them), and have our model of validation be consistent throughout.

Take a look at [Extension](#extension) to see how to build custom `Validator`s.

### Predicates
In the world of validation, predicates are simple expressions that return a `True` or `False` for a given condition. Koda Validate uses a 
class based on this concept, `Predicate`, to _enrich_ `Validator`s. Because the type and value of a `Validator`'s valid state may
differ from those of its input, it's difficult to do something like apply a list of `Validator`s to a given value:
even _if_ the types all match up, there's no assurance that the values won't change from one validator to the next. 

The role of a `Predicate` in Koda Validate is to perform additional validation _after_ the data has been verified to be 
of a specific type or shape. To this end, `Predicate`s in Koda Validate cannot change their input types or values. Let's go further with our `IntValidator`:

```python3
from koda_validate import *

int_validator = IntValidator(Min(5))

assert int_validator(6) == Valid(6)

assert int_validator(4) == Invalid(,
```
In this example `Min(5)` is a `Predicate`. As you can see the value 4
passes the `int` check but fails to pass the `Min(5)` predicate.

Because we know that predicates don't change the type or value of their inputs, we can 
sequence an arbitrary number of them together, and validate them all.

```python3
from koda_validate import *

int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

assert int_validator(12) == Valid(12)

assert int_validator(23) == Invalid(,
```
Here we have 3 `Predicate`s, but we could easily have dozens. Note that the errors from all invalid
predicates are returned. This is possible because we know that the value should be consistent from one predicate to the next.

`Predicate`s are easy to write -- take a look at [Extension](#extension) for more details.


### Processors
`Processor`s allow us to take a value of a given type and transform it into another value of that type. Processors are most useful
_after_ type validation, but _before_ predicates are checked. Here's an example:
```python3
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
cover, it aims to allow easy extension. 

Even though there is an existing `FloatValidator` in Koda Validate, we'll build our own. (Extension does not
need to be limited to new functionality; it can also be writing alternatives to the default for custom needs.)

```python3
from typing import Any
from koda_validate import *


class SimpleFloatValidator(Validator[float]):
    def __call__(self, val: Any) -> ValidationResult[float, Serializable]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(,


float_validator = SimpleFloatValidator()

test_val = 5.5

assert float_validator(test_val) == Valid(test_val)

assert float_validator(5) == Invalid(,
```

What is this doing? 
- extending `Validator`, using the following types:
  - `Any`: any type of input can be passed in to be validated
  - `float`: if the data is valid, a value of type `Valid[float]` will be returned 
  - `Serializable`: if it's invalid, a value of type `Invalid[Serializable]` will be returned
  - note that mypy understands the role of all of these types 
- the `__call__` method performs any kind of validation needed, so long as the input and output type signatures -- as determined by the `Validator` type parameters - are abided

We accept `Any` because the type of input may be unknown before submitting to the `Validator`. After our 
validation in `SimpleFloatValidator` succeeds, we know the type must be `float`. (Note that we could have coerced the value
to a `float` instead of checking its type -- that is 100% OK to do. For simplicity's sake, this validator does not coerce.)

This is all well and good, but we'll probably want to be able to validate against values of the floats, such as min, 
max, or rough equality checks. For this we use `Predicate`s. For example, if we wanted to allow a single `Predicate` in 
our `SimpleFloatValidator` we could do it like this:

```python3
from dataclasses import dataclass
from typing import Any, Optional
from koda_validate import *


@dataclass
class SimpleFloatValidator2(Validator[float]):
    predicate: Optional[Predicate[float, Serializable]] = None

    def __call__(self, val: Any) -> ValidationResult[float, Serializable]:
        if isinstance(val, float):
            if self.predicate:
                return self.predicate(val)
            else:
                return Valid(val)
        else:
            return Invalid(,

```
If `predicate` is specified, we'll check it _after_ we've verified the type of the value.

`Predicate`s are meant to validate the _value_ of a known type -- as opposed to validating at the type-level (that's what the `Validator` does). 
For example, this is how you might write and use a `Predicate` to validate a range of values:

```python3
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

Finally, let's add a `Processor`. A `Processor` is a function that takes a value of one type and then produces another 
value of that type. In our case, we want to preprocess our `float`s by converting them to their absolute value.

```python3
# (continuing from previous example)

@dataclass
class SimpleFloatValidator3(Validator[float]):
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
Note that we pre-process _after_ type checking but _before_ the predicates are run. This is the general approach 
Koda Validate takes on built-in validators. More specifically, the built-in validators expect there to be a pipeline of 
actions taken within a `Validator`: `type-check/coerce -> preprocess -> validate predicates`, where it can fail 
validation at either the first or last stage.

Note that what we've written are a number of classes that simply conform to some type constraints. It's worth remembering that
there's nothing enforcing the particular arrangement of logic we have in our `SimpleFloatValidator`. If you want to have a 
post-processing step, you can. If you want to validate an iso8601 string is a datetime, and then convert that to an unix 
epoch timestamp, and provide pre-processing, post-processing and predicates for all those steps, you can. It's important 
to remember that our `Validator`, `Predicate` (and `PredicateAsync` -- see [Async Validation](#async-validation)), and 
`Processor` objects are little more than functions with accessible metadata. You can do whatever you want with them.

## Validation Errors

In Koda Validate errors are returned as data as part of normal control flow. `Invalid` instances from built-in `Validator`s
contain JSON/YAML serializable values. (Should you build your own custom validators, there is no contract enforcing 
that constraint.) Here are a few examples of the kinds of errors you can expect to see out of the box.

```python3
from dataclasses import dataclass

from koda import Maybe

from koda_validate import *

# Wrong type
assert StringValidator()(None) == Invalid(,

# All failing `Predicate`s are reported (not just the first)
str_choice_validator = StringValidator(MinLength(2),
                                       Choices({"abc", "yz"}))

assert str_choice_validator("") == Invalid(,


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
assert city_validator(None) == Invalid(,

# Missing keys are errors
print(city_validator({}))
assert city_validator({}) == Invalid(,

# Extra keys are also errors
assert city_validator(
    {"region": "California", "population": 510, "country": "USA"}
) == Invalid(,


@dataclass
class Neighborhood:
    name: str
    city: City


neighborhood_validator = RecordValidator(
    into=Neighborhood,
    keys=(("name", StringValidator(not_blank)), ("city", city_validator)),
)

# Errors are nested in predictable manner
assert neighborhood_validator({"name": "Bushwick", "city": {}}) == Invalid(,

```
If you have any concerns about being able to handle specific types of key or object requirements, please see  
the documentation on specific validators below:
- [RecordValidator](#recordvalidator)
- [DictValidatorAny](#dictvalidatorany)
- [MapValidator](#mapvalidator)
- [OneOf2 / OneOf3](#oneof2--oneof3)
- [OptionalValidator](#optionalvalidator)
- [is_dict_validator](#is_dict_validator)
- [Lazy](#lazy)


## Async Validation
All the built-in `Validator`s in Koda are asyncio-compatible, and there is a simple, consistent way to run async validation. You 
just call a `Validator` in this form:
```python3
await validator.validate_async("abc")
```
instead of:
```python3
validator("abc")
```

(Feel free to check out [The Basics](#the-basics) and [Philosophy](#philosophy) if you are missing any context on how 
validation has been documented up to this point.)

For example, this is how you could re-use the same `StringValidator` instance in both
sync and async contexts:
```python3
import asyncio
from koda_validate import *


short_string_validator = StringValidator(MaxLength(10))

assert short_string_validator("sync") == Valid("sync")

# we're not in an async context, so we can't use `await` here; instead we use asyncio.run
assert asyncio.run(short_string_validator.validate_async("async")) == Valid("async")
```

Synchronous validators can be used in both async and sync contexts. Nonetheless, while this Validator works in async mode,
it isn't yielding any benefit for IO. It would be much more useful if we were doing something like querying a database
asynchronously:

```python3
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
                                     predicates_async=[IsActiveUsername()])

assert asyncio.run(username_validator.validate_async("michael")) == Valid("michael")

assert asyncio.run(username_validator.validate_async("tobias")) == Invalid(,

# calling in sync mode raises an AssertionError
try:
    username_validator("michael")
except AssertionError as e:
    print(e)

```
In this example we are calling the database to verify a username. A few things worth pointing out:
`PredicateAsync`s are specified in the `predicates_async` keyword argument -- separately from `Predicates`. We do this to be 
explicit -- we don't want to be confused about whether a validator requires `asyncio`. (If you try to run this validator in 
synchronous mode, it will raise an `AssertionError` -- instead make sure you call it like 
`await username_validator.validate_async("buster")`.)

Like other validators, you can nest async `Validator`s. Again, the only difference needed is to use the `.validate_async`
method of the outer-most validator.
```python3
# continued from previous example

username_list_validator = ListValidator(username_validator)

assert asyncio.run(username_list_validator.validate_async(["michael", "gob", "lindsay", "buster"])) == Valid([
  "michael", "gob", "lindsay", "buster"
])

```
You can run async validation on nested lists, dictionaries, tuples, strings, etc. All `Validator`s built into to Koda Validate
understand the `.validate_async` method. 

Koda Validate makes no assumptions about running async `Validator`s or `PredicateAsync`s concurrently; it is expected that that is
handled by the surrounding context. That is to say, async validators will not block when performing IO -- as is normal -- but if you had, say, 10 async 
predicates, they would not be run in parallel by default. This is simply because that is too much of an assumption for this library to make -- we don't 
want to accidentally send N simultaneous requests to some other service without the intent being explicitly defined. If you'd like to have `Validator`s 
or `Predicate`s run in parallel _within_ the validation step, all you should need to do is write a simple wrapper class based on either `Validator` 
or `Predicate`, implementing whatever concurrency needs you have.

For custom async `Validator`s, all you need to do is implement the `validate_async` method on a `Validator` class. There is no
separate async-only `Validator` class. This is because we might want to re-use synchronous validators in either synchronous
or asynchronous contexts. Here's an example of making a `SimpleFloatValidator` async-compatible:

```python3
import asyncio
from typing import Any

from koda_validate import *


class SimpleFloatValidator(Validator[float]):
    def __call__(self, val: Any) -> ValidationResult[float, Serializable]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(,

    # this validator doesn't do any IO, so we can just use the `__call__` method
    async def validate_async(self, val: Any) -> ValidationResult[float, Serializable]:
        return self(val)


float_validator = SimpleFloatValidator()

test_val = 5.5

assert asyncio.run(float_validator.validate_async(test_val)) == Valid(test_val)

assert asyncio.run(float_validator.validate_async(5)) == Invalid(,

```

If your `Validator` only makes sense in an async context, then you probably don't need to implement the `__call__` method. 
Instead, you'd just implement the `.validate_async` method and make sure that validator is always called by `await`-ing 
the `.validate_async` method. A `NotImplementedError` will be raised if you try to use the `__call__` method on an 
async-only `Validator`. 

## Using Metadata
One of Koda Validate's design objectives is to allow reuse of validator metadata. Principally this 
is useful in generating descriptions of the validator's constraints -- one example could be generating
an OpenAPI (or other) schema. Here we'll do something simpler and use validator metadata to build a function which can 
return plaintext descriptions of validators:

```python3
from typing import Any
from koda_validate import * 


def describe_validator(validator: Validator[Any, Any] | Predicate[Any, Any]) -> str:
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
core, they are also classes that can easily be inspected. Interpreters are the recommended way to re-use validator metadata for
non-validation purposes.


## Tour
Here are some noteworthy parts of Koda Validate explained in more detail.

### RecordValidator
`RecordValidator` is a flexible way to validate a dictionary into some other form (or back into a dictionary, if desired). It
is primarily for record-like dictionaries ([MapValidator](#mapvalidator) is recommended for map-like dictionaries).

```python3
from dataclasses import dataclass
from koda import Maybe, Just
from koda_validate import *


@dataclass
class Person:
  name: str
  age: Maybe[int]


person_validator = RecordValidator(
  into=Person,
  keys=(
    ("full name", StringValidator()),
    ("age", KeyNotRequired(IntValidator())),
  ),
)

# you can use `isinstance` in python 3.8 or 3.9 instead of `match`
match person_validator({"full name": "John Doe", "age": 30}):
    case Valid(person):
        match person.age:
            case Just(age):
                age_message = f"{age} years old"
            case nothing:
                age_message = "ageless"
        print(f"{person.name} is {age_message}")
    case Invalid(errs):
        print(errs)
```
What do we see here?
- `into=Person`: `RecordValidator` is fundamentally de-coupled from it's target -- in this case the `Person` class. It can target any
`Callable` that accepts the validated values from the keys, in the same order they are defined -- the names of the keys do not 
matter to the target. Often it will make sense to target some kind of `dataclass` or `NamedTuple` that conforms to the needed 
args, but you can use any Callable that accepts the correct arguments.
- `KeyNotRequired` results in a `Maybe` value. In the example above, age was returned as `Just(30)` because
the key was present. If the key was not present, the validation could still have succeeded, but the value for age
would be `nothing`. This gives us an explicit indication of whether a key was present or not.
- `"full name"`: keys are not bound to any kind of special form. They don't need to be strings that are valid attribute names; 
they don't even need to be strings.

`RecordValidator` is extremely flexible because it can handle any kind of dictionary key, and whether it is required or not. So,
you can validate _weird_ data like this:
```python3
from typing import List
from dataclasses import dataclass
from koda import Maybe, Just
from koda_validate import *


@dataclass
class Person:
    name: str
    age: Maybe[int]
    hobbies: List[str]


person_validator = RecordValidator(
    into=Person,
    keys=(
        (1, StringValidator()),
        (False, KeyNotRequired(IntValidator())),
        (("abc", 123), ListValidator(StringValidator()))
    ),
)

assert person_validator({
    1: "John Doe",
    False: 30,
    ("abc", 123): ["reading", "cooking"]
}) == Valid(Person(
    "John Doe",
    Just(30),
    ["reading", "cooking"]
))
```
In the opinion of this library, yes, dictionaries that use integers, bools, and tuples as keys simultaneously are _weird_. But we still
validate it :sparkles:

In `RecordValidator`, you can also validate the entire object after keys are validated by providing a `validate_object` argument.

```python3
from dataclasses import dataclass

from koda_validate import *


@dataclass
class Employee:
    title: str
    name: str


def no_dwight_regional_manager(employee: Employee) -> ValidationResult[
    Employee, Serializable]:
    if (
            "schrute" in employee.name.lower()
            and employee.title.lower() == "assistant regional manager"
    ):
        return Invalid(,
    else:
        return Valid(employee)


employee_validator = RecordValidator(
    into=Employee,
    keys=(
        ("title", StringValidator(not_blank, MaxLength(100), preprocessors=[strip])),
        ("name", StringValidator(not_blank, preprocessors=[strip])),
    ),
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)

# The fields are valid but the object as a whole is not.
assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Invalid(,

```
In this case the values of individual keys are valid, but the object as a whole is not. 

It's worth noting you can specify `validate_object_async` instead if you need to use asyncio in your validation. Remember, 
you must use the `.validate_async` method when doing any kind of async validation.

#### Limitations
`RecordValidator` is currently limited to at-most 16 keys. This is simply because mypy gets slower and slower
when typechecking against the `@overload`s for RecordValidator's `__init__` method. In the uncommon case that  
you need to validate 16+ fields on a record-like object, you may be able to use `DictValidatorAny`, `MapValidator`, or, in some cases,
`OneOf2`/`OneOf3` in combination with `RecordValidator`. There is also the possibility to generate the code into your project
if you want more keys:

```bash
# allow up to 30 keys
python /path/to/koda-validate/codegen/generate.py /your/target/directory --num-keys 30
```
  

### DictValidatorAny
`DictValidatorAny` is somewhat similar to `RecordValidator`, but there are several key differences:
- It accepts a dictionary `schema` instead of a tuple of key / value 2-tuples.
- It does not narrow the types on either the key or the value. If valid, the type of returned data will be `Dict[Any, Any]`. (This is why it has `Any` in its name.)
- It can allow for arbitrary amounts of keys
- It passes along the keys, so the validated object may appear quite similar to the input. Note that 
it will always return a new dictionary (if valid), and it is legal for values to differ from the input.

This is an equivalent example to the last `RecordValidator` example above.

```python3
from typing import Any, Dict, Hashable

from koda_validate import *


def no_dwight_regional_manager(
        employee: Dict[Hashable, Any]
) -> ValidationResult[Dict[Hashable, Any], Serializable]:
    if (
            "schrute" in employee["name"].lower()
            and employee["title"].lower() == "assistant regional manager"
    ):
        return Invalid(,
    else:
        return Valid(employee)


employee_validator = DictValidatorAny(
    {
        "title": StringValidator(not_blank, MaxLength(100), preprocessors=[strip]),
        "name": StringValidator(not_blank, preprocessors=[strip]),
    },
    # After we've validated individual fields, we may want to validate them as a whole
    validate_object=no_dwight_regional_manager,
)

assert employee_validator(
    {"name": "Jim Halpert", "title": "Sales Representative"}
) == Valid({"name": "Jim Halpert", "title": "Sales Representative"})

assert employee_validator(
    {
        "title": "Assistant Regional Manager",
        "name": "Dwight Schrute",
    }
) == Invalid(,
```

#### ListValidator
`ListValidator` validates whether some value is a list. It requires a validator to validate each item in the list. It 
can have predicates (number of items, etc.), as well as preprocessors.

```python3
from koda_validate import *

binary_list_validator = ListValidator(
    IntValidator(Choices({0, 1})),
    predicates=[MinItems(2)]
)

assert binary_list_validator([1, 0, 0, 1, 0]) == Valid([1, 0, 0, 1, 0])

assert binary_list_validator([1]) == Invalid(,

assert binary_list_validator([0, 1.0, "0"]) == Invalid(,
```
In case you're looking at the last example and wondering why the indexes `'1'` and `'2'` are strings, it's because all 
built-in validators in Koda Validate return JSON serializable data. In JSON, keys in objects are only allowed to 
be strings.


### MapValidator

`MapValidator` allows us to validate dictionaries that are mappings of one type to another type, where we don't
need to be concerned about individual keys or values:

```python3
from koda_validate import *

str_to_int_validator = MapValidator(key=StringValidator(),
                                    value=IntValidator())

assert str_to_int_validator({"a": 1, "b": 25, "xyz": 900}) == Valid(
    {"a": 1, "b": 25, "xyz": 900}
)

assert str_to_int_validator({3.14: "pi!"}) == Invalid(,
```


### OneOf2 / OneOf3

OneOfN validators are useful when you may have multiple valid shapes of data.
```python3
from koda import First, Second

from koda_validate import * 

string_or_list_string_validator = OneOf2(
    StringValidator(), ListValidator(StringValidator())
)

assert string_or_list_string_validator("ok") == Valid(First("ok"))

assert string_or_list_string_validator(["list", "of", "strings"]) == Valid(
    Second(["list", "of", "strings"])
)

```


### Tuple2Validator / Tuple3Validator

These `Validator`s work on `tuple`s as you might expect:
```python3
from koda_validate import * 

string_int_validator = Tuple2Validator(StringValidator(), IntValidator())

assert string_int_validator(("ok", 100)) == Valid(("ok", 100))

# also ok with lists
assert string_int_validator(["ok", 100]) == Valid(("ok", 100))

```


### Lazy
`Lazy`'s main purpose is to allow for the use of recursion in validation. An example use case of this might be replies
in a comment thread. This can be done with mutually recursive functions. For simplicity, here's an example of parsing a 
kind of non-empty list.

```python3
from typing import Any, Optional, Tuple

from koda_validate import *

# if enable_recursive_aliases = true in mypy
# NonEmptyList = Tuple[int, Optional["NonEmptyList"]]
NonEmptyList = Tuple[int, Optional[Any]]


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


### OptionalValidator

`OptionalValidator` is very simple. It validates a value is either `None` or passes another validator's rules.

```python3
from koda_validate import *

optional_int_validator = OptionalValidator(IntValidator())

assert optional_int_validator(5) == Valid(5)
assert optional_int_validator(None) == Valid(None)
```

### is_dict_validator

A very simple validator that only validates that and object is a dict. It doesn't do any validation against keys or
values.

```python3
from koda_validate import *

assert is_dict_validator({}) == Valid({})
assert is_dict_validator(None) == Invalid(,
assert is_dict_validator({"a": 1, "b": 2, 5: "xyz"}) == Valid({"a": 1, "b": 2, 5: "xyz"})

```

### AlwaysValid
Will always return `Valid` with the given value:
```python3
from koda_validate import *

assert always_valid(123) == Valid(123)
assert always_valid("abc") == Valid("abc")
```

## Comparison to Pydantic
Comparing Koda Validate and Pydantic is not exactly apples-to-apples, since Koda Validate is more narrowly
aimed at _just_ validation -- Pydantic has a lot of other bells and whistles. Nonetheless, this is one of the most 
common questions, and there are a number of noteworthy differences:
- **Koda Validate is built around a simple, composable definition of validation.**
- **Koda Validate treats validation as part of normal control flow.** It does not raise exceptions for invalid data.
- **Koda Validate treats validation explicitly.** It does not coerce types or mutate values in surprising ways.
- **Koda Validate is fully asyncio-compatible.**
- **Koda Validate is ~1.5 - 12x faster.** You will see differences on different versions of Python
(Python3.8 tends to show the least difference) and different systems. You can run the suite on your 
system with `python -m bench.run`. **Disclaimer that the benchmark suite is _not_ extensive.**
- **Koda Validate is pure Python.** 
- **Koda Validate is intended to empower validator documentation.** You can easily produce things like API schemas from 
`Validator`s, `Predicate`s, and `Processor`s
- **Koda Validate requires no plugins for mypy compatibility.** 
- **Pydantic has a large, mature ecosystem.** Lots of documentation, lots of searchable info on the web.
- **Pydantic focuses on having a familiar, dataclass-like syntax.** 
- **Pydantic has a lot of features Koda Validate does not.** Plugins, ORM tie-ins, etc. There will probably never be 
feature parity between the two libraries. 

## Something's Missing Or Wrong 
Open an [issue on GitHub](https://github.com/keithasaurus/koda-validate/issues) please!
