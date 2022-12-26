Extension
=========
Koda Validate aims to provide enough tools to handle most common validation needs; for the cases it doesn't
cover, it aims to allow easy extension.

Even though there is an existing ``FloatValidator`` in Koda Validate, we'll build our own
for demonstration purposes.

.. code-block:: python

    from typing import Any
    from koda_validate import *


    class SimpleFloatValidator(Validator[float]):
        def __call__(self, val: Any) -> ValidationResult[float]:
            if isinstance(val, float):
                return Valid(val)
            else:
                return Invalid(TypeErr(float), val, self)

Some notes:

- ``Validator`` is subclassed with float specified -- a value of type ``Valid[float]`` must be returned if the data passed in is valid
- ``__call__`` accepts ``Any`` because the type of input may be unknown before submitting to the ``Validator``
- ``Invalid`` is returned with all relevant validation context for downstream use, namely:

  - an error type (``TypeErr(float)``)
  - the value being validated (``val``)
  - a reference to the validator being used (``self``)

Here's how our ``Validator`` can be used:

.. code-block::

    float_validator = SimpleFloatValidator()

    float_validator(5.5)
    # > Valid(5.5)

    float_validator(5)
    # > Invalid(TypeErr(float), 5, ...)


This is all well and good, but we'll probably want to be able to validate against ``float``
values, such as min, max, or rough equality checks. For this we use ``Predicate``s. For
example, if we wanted to allow a single ``Predicate`` in our ``SimpleFloatValidator`` we
could do so like this:

.. code-block:: python


    from dataclasses import dataclass
    from typing import Any, Optional
    from koda_validate import *


    class SimpleFloatValidatorWithPredicate(Validator[float]):
        def __init__(self, predicate: Optional[Predicate[float]] = None) -> None:
            self.predicate = predicate

        def __call__(self, val: Any) -> ValidationResult[float]:
            if isinstance(val, float):
                if self.predicate(val):
                    return Valid(val)
                else:
                    return Invalid(PredicateErrs([self.predicate]), val, self)
            else:
                return Invalid(TypeErr(float), val, self)

If ``predicate`` is specified, we'll check it *after* we've verified the type of the value.

``Predicate``\s are meant to validate the *value* of a known type -- as opposed to validating at the type-level (that's what the ``Validator`` does).
For example, this is how you might write and use a ``Predicate`` to validate a range of values:
