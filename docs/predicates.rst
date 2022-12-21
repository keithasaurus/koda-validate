Predicates
----------
In the world of validation, predicates are simple expressions that return a ``True`` or ``False`` for a given condition. Koda Validate uses a
class based on this concept, ``Predicate``, to *enrich* ``Validator``\s. Because the type and value of a ``Validator``\'s valid state may
differ from those of its input, it's difficult to do something like apply a list of ``Validator``\s to a given value:
even *if* the types all match up, there's no assurance that the values won't change from one validator to the next.

The role of a ``Predicate`` in Koda Validate is to perform additional validation *after* the data has been verified to be
of a specific type or shape(whether through a simple check or through coercion). To this end, ``Predicate``\s in
Koda Validate cannot change their input types or values. Let's go further with our ``IntValidator``\:

.. code-block:: python

    from koda_validate import *

    int_validator = IntValidator(Min(5))

    assert int_validator(6) == Valid(6)

    assert int_validator(4) == Invalid(PredicateErrs([Min(5)]), 4, IntValidator(Min(5)))

In this example `Min(5)` is a `Predicate`. As you can see the value 4
passes the `int` type check but fails to pass the `Min(5)` predicate.

Because we know that predicates don't change the type or value of their inputs, we can
sequence an arbitrary number of them together, and validate them all.

.. code-block:: python

    from koda_validate import *
    from koda_validate import PredicateErrs

    int_validator = IntValidator(Min(5), Max(20), MultipleOf(4))

    assert int_validator(12) == Valid(12)

    assert int_validator(23) == Invalid(
        PredicateErrs([Max(20), MultipleOf(4)]), 23, int_validator
    )

Here we have 3 ``Predicate``\s, but we could easily have dozens. Note that Predicates for which the
value is invalid are returned within a ``PredicateErrs`` instance. We are only able to return all the
failing ``Predicate``\s because we know that the value will be consistent from one predicate to the next.

``Predicate``\s are easy to write -- take a look at [Extension](#extension) for more details.


## Extension
Koda Validate aims to provide enough tools to handle most common validation needs; for the cases it doesn't
cover, it aims to allow easy extension.

Even though there is an existing ``FloatValidator`` in Koda Validate, we'll build our own. (Extension does not
need to be limited to new functionality; it can also be writing alternatives to the default for custom needs.)

.. code-block:: python

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
If `predicate` is specified, we'll check it *after* we've verified the type of the value.

`Predicate`s are meant to validate the *value* of a known type -- as opposed to validating at the type-level (that's what the `Validator` does).
For example, this is how you might write and use a `Predicate` to validate a range of values:
