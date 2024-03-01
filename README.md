# Koda Validate

Koda Validate is a library and toolkit for building composable and typesafe validators. In many cases,
validators can be derived from typehints (e.g. TypedDicts, dataclasses, and NamedTuples). For everything else, you can 
combine existing validation logic, or write your own. At its heart, Koda Validate is just a few kinds of
callables that fit together, so the possibilities are endless. It is async-friendly and comparable in performance to Pydantic 2.

Koda Validate can be used in normal control flow or as a runtime type checker.

Docs: [https://koda-validate.readthedocs.io/en/stable/](https://koda-validate.readthedocs.io/en/stable/)

## At a Glance

#### Explicit Validators

```python
from koda_validate import ListValidator, StringValidator, MaxLength, MinLength

my_string_validator = StringValidator(MinLength(1), MaxLength(20))
my_string_validator("a string!")
#> Valid("a string!")
my_string_validator(5)
#> Invalid(...)


# Composing validators
list_string_validator = ListValidator(my_string_validator)
list_string_validator(["a", "b", "c"])
#> Valid(["a", "b", "c"])
```

#### Derived Validators

```python
from typing import TypedDict
from koda_validate import (TypedDictValidator, Valid, Invalid)
from koda_validate.serialization import to_serializable_errs

class Person(TypedDict):
    name: str
    hobbies: list[str]


person_validator = TypedDictValidator(Person)

match person_validator({"name": "Guido"}):
    case Valid(string_list):
        print(f"woohoo, valid!")
    case Invalid() as invalid:
        # readable errors
        print(to_serializable_errs(invalid))

#> {'hobbies': ['key missing']}
```

#### Runtime Type Checking

```python
from koda_validate.signature import validate_signature

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

There's much, much more in the [Docs](https://koda-validate.readthedocs.io/en/stable/).


## Something's Missing or Wrong 
Open an [issue on GitHub](https://github.com/keithasaurus/koda-validate/issues) please!
