# Koda Validate

- type-driven
- composable
- extensible
- async-compatible

Build validators automatically (from typehints) or explicitly. Combine them to build 
validators of arbitrary complexity.

Docs: [https://koda-validate.readthedocs.io/en/latest/](https://koda-validate.readthedocs.io/en/latest/)

```python

from typing import TypedDict 
from koda_validate import *

# Explicit Validators
string_validator = StringValidator(MinLength(8), MaxLength(20))

list_string_validator = ListValidator(string_validator)


# Derived Validators
class Person(TypedDict):
    name: str
    hobbies: list[str] 

person_validator = TypedDictValidator(Person)

```

There's much, much more... Check out the [Docs](https://koda-validate.readthedocs.io/en/latest/).


## Something's Missing Or Wrong 
Open an [issue on GitHub](https://github.com/keithasaurus/koda-validate/issues) please!
