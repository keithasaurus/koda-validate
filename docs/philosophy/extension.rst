Extension
=========
Koda Validate aims to provide enough tools to handle most common validation needs; for the cases it doesn't
cover, it aims to allow easy extension.

Even though there is an existing ``FloatValidator`` in Koda Validate, we'll build our own. (Extension does not
need to be limited to new functionality; it can also be writing alternatives to the default for custom needs.)

.. code-block:: python

    from typing import Any

    from koda_validate import *

    class SimpleFloatValidator(Validator[float]):
        def __call__(self, val: Any) -> ValidationResult[float]:
            if isinstance(val, float):
                return Valid(val)
            else:
                return Invalid(TypeErr(float), val, self)

    float_validator = SimpleFloatValidator()

    test_val = 5.5

    float_validator(test_val)
    # > Valid(test_val)

    float_validator(5)
    # > Invalid(TypeErr(float), 5, ...)


What is this doing?
- extending ``Validator``, where a value of type ``Valid[float]`` will be returned if the data passed in is valid
- implementing the `__call__` method, so the class instances can be called like ``function``s when validating
- ``__call__`` accepts ``Any`` because the type of input may be unknown before submitting to the ``Validator``. (After our
validation in ``SimpleFloatValidator`` succeeds, we know the type must be ``float``)

This is all well and good, but we'll probably want to be able to validate against values of the floats, such as min,
max, or rough equality checks. For this we use ``Predicate``s. For example, if we wanted to allow a single ``Predicate`` in
our ``SimpleFloatValidator`` we could do it like this:

.. code-block:: python


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
                return Invalid(TypeErr(float), val, self)

If ``predicate`` is specified, we'll check it *after* we've verified the type of the value.

``Predicate``\s are meant to validate the *value* of a known type -- as opposed to validating at the type-level (that's what the ``Validator`` does).
For example, this is how you might write and use a ``Predicate`` to validate a range of values:
