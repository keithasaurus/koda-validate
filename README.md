# Koda Validate

Koda Validate is a library and toolkit for building composable and typesafe validators. In many cases,
validators can be derived from typehints (e.g. `TypeDict`s, `@dataclass`es, `NamedTuples`). For everything else, you can 
combine existing validation logic, or write your own. At its heart, Koda Validate is just a few kinds of
callables that fit together, so the possibilities are as endless as the kinds of functions 
you can write. It is async-friendly and comparable in performance to Pydantic 2.

Koda Validate can be used in normal control flow or as a runtime type checker.

Docs: [https://koda-validate.readthedocs.io/en/stable/](https://koda-validate.readthedocs.io/en/stable/)

### At a Glance 

```python

from typing import TypedDict
from koda_validate import (StringValidator, MaxLength, MinLength,
                           ListValidator, TypedDictValidator, Valid, Invalid)
from koda_validate.serialization import to_serializable_errs
from koda_validate.signature import validate_signature


# Explicit Validators
string_validator = StringValidator(MinLength(8), MaxLength(20))

list_string_validator = ListValidator(string_validator)


# Automatic Validators
class Person(TypedDict):
    name: str
    hobbies: list[str]


person_validator = TypedDictValidator(Person)

# Produce readable errors
match person_validator({"name": "Guido"}):
    case Valid(string_list):
        print(f"woohoo, valid!")
    case Invalid() as invalid:
        print(to_serializable_errs(invalid))

# prints: {'hobbies': ['key missing']}


# Runtime type checking
@validate_signature
def add(a: int, b: int) -> int:
    return a + b


add(1, 2)  # returns 3

add(1, "2")  # raises `InvalidArgsError`
# koda_validate.signature.InvalidArgsError:
# Invalid Argument Values
# -----------------------
# b='2'
#     expected <class 'int'>

```

There's much, much more... Check out the [Docs](https://koda-validate.readthedocs.io/en/stable/).


## Something's Missing or Wrong 
Open an [issue on GitHub](https://github.com/keithasaurus/koda-validate/issues) please!
