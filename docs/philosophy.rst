Philosophy
==========
At it's core, Koda Validate is based on a few simple ideas about what validation _is_. This
allows Koda Validate to be extended to validate essentially any kind of data. It also generally allows for 
less code, and clearer paths to optimization than other approaches.

Validators
----------

In Koda Validate, `Validator` is the fundamental validation building block. It's based on the idea that
validation can be universally represented by the function signature (pseudocode):
.. code-block::

    InputType -> ValidType | InvalidType

In Koda Validate (and Python) this looks more like:

.. code-block:: python

    Callable[[Any], Union[Valid[ValidType], Invalid]]

    # it's shorter when using the ValidationResult type alias
    Callable[[Any], ValidationResult[ValidType]]


A quick example:

.. code-block:: python

    from koda_validate import IntValidator, Valid, Invalid, TypeErr

    int_validator = IntValidator()

    assert int_validator(5) == Valid(5)
    assert int_validator("not an integer") == Invalid(TypeErr(int), 5, IntValidator())


This is a useful model to have for validation, because it means we can combine
validators in different ways (i.e. nesting them), and have our model of validation be consistent throughout.

Take a look at Extension to see how to build custom `Validator`s.

Predicates
----------
In the world of validation, predicates are simple expressions that return a `True` or `False` for a given condition. Koda Validate uses a
class based on this concept, `Predicate`, to _enrich_ `Validator`s. Because the type and value of a `Validator`'s valid state may
differ from those of its input, it's difficult to do something like apply a list of `Validator`s to a given value:
even _if_ the types all match up, there's no assurance that the values won't change from one validator to the next.

The role of a `Predicate` in Koda Validate is to perform additional validation _after_ the data has been verified to be
of a specific type or shape(whether through a simple check or through coercion). To this end, `Predicate`s in
Koda Validate cannot change their input types or values. Let's go further with our `IntValidator`:

```python3
from koda_validate import *

int_validator = IntValidator(Min(5))

assert int_validator(6) == Valid(6)

assert int_validator(4) == Invalid(PredicateErrs([Min(5)]), 4, IntValidator(Min(5)))
```
In this example `Min(5)` is a `Predicate`. As you can see the value 4
passes the `int` type check but fails to pass the `Min(5)` predicate.

Because we know that predicates don't change the type or value of their inputs, we can
sequence an arbitrary number of them together, and validate them all.

```python3
from koda_validate import *
from koda_validate import PredicateErrs

int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

assert int_validator(12) == Valid(12)

assert int_validator(23) == Invalid(
    PredicateErrs([Max(20), MultipleOf(4)]), 23, int_validator
)

```
Here we have 3 `Predicate`s, but we could easily have dozens. Note that Predicates for which the
value is invalid are returned within a `PredicateErrs` instance. We are only able to return all the
failing `Predicate`s because we know that the value will be consistent from one predicate to the next.

`Predicate`s are easy to write -- take a look at [Extension](#extension) for more details.


### Processors
`Processor`s allow us to take a value of a given type and transform it into another value of that type. `Processor`s are most useful
_after_ type validation, but _before_ predicates are checked. They tend to be more useful on strings than any other type:
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
from koda_validate import TypeErr, ValidationResult


class SimpleFloatValidator(Validator[float]):
    def __call__(self, val: Any) -> ValidationResult[float]:
        if isinstance(val, float):
            return Valid(val)
        else:
            return Invalid(TypeErr(float), val, self)


float_validator = SimpleFloatValidator()

test_val = 5.5

assert float_validator(test_val) == Valid(test_val)

assert float_validator(5) == Invalid(TypeErr(float), 5, float_validator)

```

What is this doing?
- extending `Validator`, where a value of type `Valid[float]` will be returned if valid
- implementing the `__call__` method where (synchronous) validation is expected to be performed
- __call__ accepts `Any` because the type of input may be unknown before submitting to the `Validator`. (After our
validation in `SimpleFloatValidator` succeeds, we know the type must be `float`)

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
