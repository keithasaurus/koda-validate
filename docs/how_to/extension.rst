Extension
=========
Koda Validate aims to provide enough tools to handle most common validation needs; for
the cases it doesn't cover, it aims to allow easy extension.

.. module:: koda_validate

Validators
----------

We'll build a simple :class:`Validator` for ``float`` values to demonstrate how :class:`Validator`\s
are built.

.. code-block:: python

    from typing import Any
    from koda_validate import *


    class SimpleFloatValidator(Validator[float]):
        # `__call__` allows a `SimpleFloatValidator` instance to be called like a function
        def __call__(self, val: Any) -> ValidationResult[float]:
            if isinstance(val, float):
                return Valid(val)
            else:
                return Invalid(TypeErr(float), val, self)

Some notes:

- :class:`Validator` is subclassed and parameterized with ``float``. This just means a value of type ``Valid[float]`` must be returned when valid
- ``__call__`` accepts ``Any`` because the type of input may be unknown before submitting to the :class:`Validator`
- :class:`Invalid` is returned with all relevant validation context for downstream use, namely:

  - an error type (``TypeErr(float)``)
  - the value being validated (``val``)
  - a reference to the validator being used (``self``)

Here's how our :class:`Validator` can be used:

.. code-block:: python

    float_validator = SimpleFloatValidator()

    float_validator(5.5)
    # > Valid(5.5)

    float_validator(5)
    # > Invalid(TypeErr(float), 5, ...)

Predicates
----------
When we want to perform additional refinement against a value, we use :class:`Predicate`\s. In
the case of ``float``, we might want to check things like min, max, or fuzzy equality.
We'll make a ``FloatMin`` :class:`Predicate` to validate that ``float`` values are above some
threshold:

.. code-block:: python

    class FloatMin(Predicate[float]):
        def __init__(self, min: float) -> None:
            self.min = min

        def __call__(self, val: float) -> bool:
            return val >= self.min

We can use ``FloatMin`` on its own, but it's not terribly useful.

.. code-block:: python

    min_5 = FloatMin(5.0)

    min_5(5.678)
    # > True

    min_6(1.23)
    # > False

:class:`Predicate`\s are more useful when we allow them to work with :class:`Validator`\s. For simplicity,
we'll allow just one.

.. code-block:: python


    from dataclasses import dataclass
    from typing import Any, Optional
    from koda_validate import *


    class SimpleFloatValidator(Validator[float]):
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

In the code above, if :class:`Predicate<koda_validate.Predicate>` is specified, we'll check it *after* we've verified the type of the value.

.. code-block:: python

    validator = SimpleFloatValidator(FloatMin(2.5))

    validator(3.14)
    # > Valid(3.14)

    validator(1.1)
    # > Invalid(PredicateErrs([FloatMin(2.5)]), 1.1, ...)

We limited the Validator to one :class:`Predicate` for simplicity. In Koda Validate, :class:`Validator`\s
that accept predicates typically allow of a ``List`` of :class:`Predicate`\s. Because :class:`Predicate`\s
cannot alter values, it's safe to have as many as you want (i.e. ``SimpleFloatValidator(FloatMin(3.3), FloatMax(4.4), ...)``).


Processors
----------
We can also conforming values using processors. For this example, we'll say we want to
convert ``float``\s to their absolute value before we validate it.

.. code-block:: python

    class FloatAbs(Processor[float]):
        def __call__(self, val: float) -> float:
            return abs(val)

To allow a processor to be this to our :class:`Validator`, we can change the code similarly to
how we did with a :class:`Predicate`.

.. code-block:: python

    class SimpleFloatValidator(Validator[float]):
        def __init__(self,
                     predicate: Optional[Predicate[float]] = None,
                     preprocessor: Optional[Processor[float]] = None) -> None:
            self.predicate = predicate
            self.preprocessor = preprocessor

        def __call__(self, val: Any) -> ValidationResult[float]:
            if isinstance(val, float):
                if self.preprocessor:
                    val = self.preprocessor(val)

                if self.predicate(val):
                    return Valid(val)
                else:
                    return Invalid(PredicateErrs([self.predicate]), val, self)
            else:
                return Invalid(TypeErr(float), val, self)


    validator = SimpleFloatValidator(predicate=FloatMin(2.2),
                                     preprocessor=FloatAbs())

    validator(-5.5)
    # > Valid(5.5)


Async
-----
There are only a few things to do differently if we want to make this :class:`Validator<koda_validate.Validator>` work
asynchronously:

- implement a ``validate_async`` method on the Validator (which should be very similar to the existing ``__call__`` method)
- if desired, allow for :class:`PredicateAsync<koda_validate.PredicateAsync>` predicates to be passed in

Then when you use the Validator in an async context, you just need to call it like:

.. code-block:: python

    validator = SimpleFloatValidator(...)
    await validator.validate_async(5.5)


.. note::
    It's important to mention that you can build :class:`Validator<koda_validate.Validator>`\s, :class:`Predicate<koda_validate.Predicate>`\s, and
    :class:`Processor<koda_validate.Processor>`\s to be initialized with any combination of attributes you want. The only
    contracts for these kinds of objects are on the ``__call__`` and ``validate_async``
    methods; otherwise you have complete freedom to structure the logic as you see fit.

This discussion has focused on extension only in terms of what we can validate. To learn
more about how we inspect validators to add new capabilities, check out Metadata.