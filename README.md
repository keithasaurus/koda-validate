# Koda Validate

Koda validate is a typesafe validation library built on top of [koda](https://pypi.org/project/koda/). This project
aims to facilitate:
- straightforward combination of validators
- type-based code quality assurance
- ability to produce schemas from validator metadata

# Quickstart
Let's start as simple as possible.

```python3
from koda import Ok
from koda_validate.validators import StringValidator, Err

string_validator = StringValidator()

assert string_validator("s") == Ok("s")
assert string_validator(None) == Err(["expected a string"])
```

Testing if something is a string can be useful, but we often want to constrain values in some way.

```python
from koda import Ok
from koda_validate.validators import StringValidator, Err, not_blank, MinLength

string_validator = StringValidator(not_blank, MinLength(5))

assert string_validator("  ") == Err(["cannot be blank", "minimum allowed length is 5"])
assert string_validator("long enough") == Ok("long enough")
```
Note that we return errors from all failing value-level validators, instead of 
failing and exiting on the first error. This is possible because of certain type-level guarantees within
Koda Validate, but we'll get into that later.

One thing to note is that we can express validators with
multiple acceptable types. A common need is to be able to express
values that can be some concrete type or `None`. For this case we
have `Nullable`

```python
from koda_validate import Nullable, IntValidator
Nullable(IntegerValidator())
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
