# Koda Validate

Build typesafe validators automatically or explicitly -- or write your own. Combine them to
build validators of arbitrary complexity. Koda Validate is async-friendly, pure Python, and
1.5x - 12x faster than Pydantic.

Docs: [https://koda-validate.readthedocs.io/en/stable/](https://koda-validate.readthedocs.io/en/stable/)

```python

from typing import TypedDict
from koda_validate import (StringValidator, MaxLength, MinLength,
                           ListValidator, TypedDictValidator, Valid, Invalid)
from koda_validate.serialization import to_serializable_errs
from koda_validate.signature import validate_signature


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


# Explicit Validators
string_validator = StringValidator(MinLength(8), MaxLength(20))

list_string_validator = ListValidator(string_validator)


# Runtime type checking
@validate_signature
def add(a: int, b: int) -> int:
    return a + b

```

There's much, much more... Check out the [Docs](https://koda-validate.readthedocs.io/en/stable/).


## Something's Missing Or Wrong 
Open an [issue on GitHub](https://github.com/keithasaurus/koda-validate/issues) please!
